# backend/app/shared_services/llm_service/llm_service.py
"""Multi-Model LLM Orchestration Service with Free Tier & High-Availability Optimization.

Supports:
1. Meta Model API (Muse Spark 1.3) via https://api.meta.ai/v1
2. Google Gemini Flash (Free Tier)
3. Pollinations AI (Zero-auth, 100% free OpenAI-compatible endpoint)
4. Dynamic Contextual Heuristic Synthesizer (Zero-downtime offline fallback with topic-derived scripts)
"""

import asyncio
import json
import logging
import re
from typing import Type, TypeVar, Dict, Any, Optional
import httpx
from pydantic import BaseModel, ValidationError
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from google.generativeai.types.safety_types import HarmBlockThreshold, HarmCategory
from app.core.config import settings

logger = logging.getLogger("app.llm_service")
T = TypeVar("T", bound=BaseModel)


def clean_json_response(text: str) -> str:
    """Remove markdown code blocks and extract valid JSON payload."""
    cleaned = re.sub(r"^```(?:json)?\s*", "", text.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end != -1:
        return cleaned[start : end + 1]
    return cleaned


_META_DISABLED = False

async def call_meta_muse_api(prompt: str, format_instructions: str) -> Optional[str]:
    """Call Meta Model API (Muse Spark) via OpenAI-compatible endpoint."""
    global _META_DISABLED
    if _META_DISABLED:
        return None
    api_key = settings.META_API_KEY
    if not api_key:
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": "muse-spark-1.3",
        "messages": [
            {
                "role": "system",
                "content": f"You are an expert video screenwriter. Always respond strictly in valid JSON format matching the schema.\n{format_instructions}",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": settings.TEMPERATURE,
    }

    try:
        async with httpx.AsyncClient(timeout=8.0) as client:
            res = await client.post(
                f"{settings.META_API_BASE}/chat/completions",
                json=payload,
                headers=headers,
            )
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            elif res.status_code in (401, 402, 403):
                _META_DISABLED = True
                logger.warning(
                    f"Meta Model API authentication/billing disabled (status {res.status_code}). Switching to zero-cost cloud LLM."
                )
            else:
                logger.warning(
                    f"Meta Model API returned status {res.status_code}: {res.text[:100]}. Falling back."
                )
    except Exception as e:
        logger.warning(f"Meta Model API request failed: {e}. Falling back.")
    return None


async def call_gemini_api(
    prompt: str,
    response_model: Type[T],
    model_name: Optional[str] = None,
) -> Optional[str]:
    """Call Google Gemini model."""
    if not settings.GEMINI_API_KEY:
        return None

    try:
        llm = ChatGoogleGenerativeAI(
            model=model_name or settings.GEMINI_MODEL,
            google_api_key=settings.GEMINI_API_KEY,
            generation_config={
                "temperature": settings.TEMPERATURE,
                "max_output_tokens": settings.MAX_OUTPUT_TOKENS,
                "top_p": settings.TOP_P,
                "top_k": settings.TOP_K,
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            },
        )

        parser = PydanticOutputParser(pydantic_object=response_model)
        prompt_template = PromptTemplate(
            input_variables=["input"],
            template="{input}\n\n{format_instructions}",
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
        chain = prompt_template | llm | StrOutputParser()
        return await chain.ainvoke({"input": prompt})
    except Exception as e:
        logger.warning(f"Gemini API invocation failed: {e}")
        return None


async def call_pollinations_api(prompt: str, format_instructions: str) -> Optional[str]:
    """Call Pollinations AI free OpenAI-compatible endpoint with fast timeout."""
    payload = {
        "model": "openai",
        "messages": [
            {
                "role": "system",
                "content": f"You are an expert viral video screenwriter. Always respond strictly in valid JSON format matching the schema.\n{format_instructions}",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.7,
    }
    try:
        async with httpx.AsyncClient(timeout=12.0) as client:
            res = await client.post(
                "https://text.pollinations.ai/openai/chat/completions",
                json=payload,
                headers={"Content-Type": "application/json"}
            )
            if res.status_code == 200:
                data = res.json()
                return data["choices"][0]["message"]["content"]
            else:
                logger.warning(f"Pollinations AI returned {res.status_code}: {res.text[:100]}")
    except Exception as e:
        logger.warning(f"Pollinations AI request failed: {e}")
    return None


async def invoke_llm_with_prompt(
    prompt: str,
    response_model: Type[T],
    model_name: Optional[str] = None,
    max_retries: Optional[int] = None,
) -> Dict[str, Any]:
    """Invoke Multi-Model LLM with Pydantic validation and automatic cascade fallback."""
    if not response_model:
        raise ValueError("response_model is required")

    parser = PydanticOutputParser(pydantic_object=response_model)
    format_instructions = parser.get_format_instructions()

    # 1. Try Meta Model API (Muse Spark) if configured
    if settings.META_API_KEY and not _META_DISABLED:
        ai_response = await call_meta_muse_api(prompt, format_instructions)
        if ai_response:
            cleaned = clean_json_response(ai_response)
            try:
                return parser.parse(cleaned).model_dump()
            except Exception:
                try:
                    pj = json.loads(cleaned)
                    if isinstance(pj, dict):
                        return pj
                except Exception:
                    pass

    # 2. Try Google Gemini if configured
    if settings.GEMINI_API_KEY:
        try:
            ai_response = await call_gemini_api(prompt, response_model, model_name)
            if ai_response:
                cleaned = clean_json_response(ai_response)
                try:
                    return parser.parse(cleaned).model_dump()
                except Exception:
                    try:
                        pj = json.loads(cleaned)
                        if isinstance(pj, dict):
                            return pj
                    except Exception:
                        pass
        except Exception as e:
            logger.warning(f"Gemini API error: {e}")

    # 3. Try Pollinations AI (Zero-auth, free cloud LLM)
    ai_response = await call_pollinations_api(prompt, format_instructions)
    if ai_response:
        cleaned = clean_json_response(ai_response)
        try:
            return parser.parse(cleaned).model_dump()
        except Exception:
            try:
                pj = json.loads(cleaned)
                if isinstance(pj, dict):
                    return pj
            except Exception:
                pass

    # 4. Autonomous Dynamic Heuristic Synthesizer Fallback (Zero-Downtime Guarantee)
    logger.info("Engaging dynamic topic-aware heuristic script generator fallback.")
    return synthesize_autonomous_script(prompt, response_model)


def extract_topic_from_prompt(prompt: str) -> str:
    """Intelligently extract the topic from various prompt styles."""
    patterns = [
        r'about ["\'](.*?)["\']',
        r'discussing ["\'](.*?)["\']',
        r'explain ["\'](.*?)["\']',
        r'Theme:\s*(.*)',
        r'topic:\s*(.*)',
        r'about (.*?)(?:\.|\n|\r|$)',
        r'explain (.*?)(?:\.|\n|\r|$)',
    ]
    for pat in patterns:
        m = re.search(pat, prompt, re.IGNORECASE)
        if m:
            clean = m.group(1).strip().strip('"\'')
            if clean and len(clean) > 2:
                return clean
    return "Quantum Physics & Modern Science"


def synthesize_autonomous_script(prompt: str, response_model: Type[T]) -> Dict[str, Any]:
    """Autonomous dynamic synthesizer ensuring 100% uptime and topic-specific variety."""
    model_name_str = getattr(response_model, "__name__", "")
    topic = extract_topic_from_prompt(prompt)

    # Dynamic seed based on topic string to ensure consistent yet bespoke variations
    seed = sum(ord(c) for c in topic)

    peter_hooks = [
        f"Holy crap! Did you know about {topic}? It completely rewrote my entire understanding of reality!",
        f"Guys, stop scrolling! Look into {topic} right now—I tried explaining it to Lois and her brain short-circuited!",
        f"Wait, wait, wait! Nobody ever warned me that {topic} was actually real! This changes everything!",
        f"Check this out! So I was looking into {topic}, and it turns out everything we were taught was backwards!"
    ]
    stewie_retorts = [
        f"Quiet, you gargantuan simpleton. What Peter is clumsily fumbling over regarding {topic} is actually governed by elegant principles.",
        f"Silence, you corpulent buffoon! {topic} isn't magic—it's a demonstrable phenomenon that requires a modicum of intellect to appreciate.",
        f"Oh cease your vacuous bleating, fat man. The fundamental truth of {topic} is far more devastating to your simplistic worldview.",
        f"Must you butcher scientific inquiry, Peter? The real mechanics of {topic} dictate how systems interact under stress."
    ]
    brian_insights = [
        f"Actually Stewie, peer-reviewed research on {topic} shows fascinating implications for both technology and human consciousness.",
        f"Well, if you actually study {topic}, researchers found that observing the system directly alters its underlying behaviour.",
        f"Historically speaking, the breakthrough discoveries surrounding {topic} unlocked technologies we literally rely on every single day.",
        f"To be fair, {topic} isn't just theory anymore—modern engineering harnesses it to solve problems previously thought impossible."
    ]
    peter_comedies = [
        f"Yeah! Like that time I tried using {topic} to sneak out of Sunday church without anyone noticing!",
        f"Exactly! Which means if I apply {topic} to my diet, bacon technically has negative calories!",
        f"Sweet! See? Even Brian agrees! If we weaponize {topic}, we can dominate Quahog by next Tuesday!",
        f"See? I told ya! Now where do I buy a five-pound bucket of {topic} before Amazon sells out?"
    ]
    stewie_closings = [
        f"Blast you, Peter, that is completely absurd. If anyone needs me, I shall be recalibrating my particle accelerator.",
        f"Remarkable. Even in the face of profound knowledge about {topic}, you remain stubbornly immune to intelligence.",
        f"Victory shall be mine, regardless of how many times you misuse {topic}, you lumbering potato.",
        f"Save your breath, Brian. The algorithm has already captivated their fleeting human attention spans anyway."
    ]
    brian_ctas = [
        f"Hit follow if you want to understand how {topic} actually impacts your life. Drop your thoughts below!",
        f"Subscribe for more breakdowns on {topic} and the real science behind modern breakthroughs!",
        f"Let us know in the comments: do you think {topic} is a blessing or a curse for humanity?",
        f"Follow for more real science explained through cartoon madness. Which topic should we tackle next?"
    ]

    p_hook = peter_hooks[seed % len(peter_hooks)]
    s_retort = stewie_retorts[(seed + 1) % len(stewie_retorts)]
    b_insight = brian_insights[(seed + 2) % len(brian_insights)]
    p_comedy = peter_comedies[(seed + 3) % len(peter_comedies)]
    s_closing = stewie_closings[(seed + 4) % len(stewie_closings)]
    b_cta = brian_ctas[(seed + 5) % len(brian_ctas)]

    fields = getattr(response_model, "model_fields", {})
    if model_name_str == "VideoScript" or "dialogues" in fields:
        return {
            "topic": topic,
            "dialogues": [
                {
                    "character": "Peter",
                    "text": p_hook,
                    "infographic": f"Overview of {topic[:30]}",
                    "mood_descriptor": "excited",
                },
                {
                    "character": "Stewie",
                    "text": s_retort,
                    "infographic": f"Core Mechanics: {topic[:25]}",
                    "mood_descriptor": "sarcastic",
                },
                {
                    "character": "Brian",
                    "text": b_insight,
                    "infographic": f"Scientific Research Data",
                    "mood_descriptor": "intellectual",
                },
                {
                    "character": "Peter",
                    "text": p_comedy,
                    "infographic": None,
                    "mood_descriptor": "confused",
                },
                {
                    "character": "Stewie",
                    "text": s_closing,
                    "infographic": "Final Conclusion",
                    "mood_descriptor": "condescending",
                },
                {
                    "character": "Brian",
                    "text": b_cta,
                    "infographic": "Follow & Comment",
                    "mood_descriptor": "neutral",
                },
            ],
        }
    elif model_name_str == "AffirmationList" or "affirmations" in fields:
        return {
            "theme": topic,
            "category": "resonance",
            "affirmations": [
                f"I am fully aligned with peace, clarity, and the natural power of {topic}.",
                "My mind is calm, centered, and deeply focused in this present moment.",
                f"I absorb wisdom and creative inspiration through {topic}.",
                "Every breath expands my capacity for focus, growth, and inner harmony.",
            ],
        }

    return {"error": "All LLM providers and retries exhausted"}
