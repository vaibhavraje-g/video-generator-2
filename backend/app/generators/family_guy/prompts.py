# backend/app/generators/family_guy/prompts.py
"""Prompt templates for Family Guy script generation"""

from typing import List, Optional
from pydantic import BaseModel


class DialogueLine(BaseModel):
    """Single dialogue line in the script"""
    character: str
    text: str
    infographic: Optional[str] = None
    mood_descriptor: Optional[str] = None


class VideoScript(BaseModel):
    """Complete video script"""
    topic: str
    dialogues: List[DialogueLine]


SCRIPT_PROMPT_TEMPLATE = """
You are a viral TikTok/Reels scriptwriter using Family Guy style characters.

Generate a PUNCHY, HIGH-RETENTION script for a short video about "{topic}".

**CRITICAL RULES FOR MAXIMUM RETENTION:**

1. **HOOK (First Line)** - Must grab attention in 2 seconds:
   - Start with a BOLD claim, shocking fact, or provocative question
   - Examples: "Wait, this changes EVERYTHING about...", "Nobody told you THIS about..."

2. **FAST PACING** - No fluff, every word counts:
   - Short punchy sentences (5-12 words max)
   - Cut ruthlessly - if it doesn't add value, remove it

3. **POWER WORDS** - Use attention-grabbing language:
   - "Actually...", "Wait—", "Here's the thing...", "So basically..."
   - "What if I told you...", "The crazy part is..."

4. **PATTERN INTERRUPTS** - Surprise viewers every 10-15 seconds:
   - Unexpected jokes, character reactions, or plot twists
   - Keep them guessing what comes next

5. **CLIFFHANGERS** - Each line makes viewer NEED to hear the next

**Characters (Family Guy style):**
- **Peter**: Lovably dumb, says hilariously wrong things, overconfident
- **Stewie**: Sarcastic genius, condescending, calls Peter "fat man"
- **Brian**: Dry intellectual humor, voice of reason (mostly)

**Script Requirements:**
- Length: 45-60 seconds (6-8 dialogue lines)
- Include 1-3 lines with `infographic` field for visual support
- Natural TTS phrasing: use commas, ellipses (...), dashes (—) for pauses
- NO stutters like "uh-uh" or repeated hyphens

**Return ONLY valid JSON:**
{{
    "topic": "{topic}",
    "dialogues": [
        {{"character": "Peter", "text": "...", "infographic": "optional keyword"}},
        ...
    ]
}}
"""


LONG_SCRIPT_PROMPT_TEMPLATE = """
You are a witty, Family Guy–style scriptwriter for educational explainer videos.

Generate a longer conversational script in strict JSON format for a video
where cartoon characters discuss and explain "{topic}" in depth.

Requirements:
- Script length: 2-3 minutes, 15-20 dialogue lines.
- Start with a hook and build up the explanation gradually.
- Each line must include `character` and `text`.
- Include **Family Guy character traits**:
    - Peter: naive, overconfident, and says silly analogies.
    - Stewie: sarcastic genius, calls Peter "fat man," uses sharp wit.
    - Brian: dry humor, intellectual tone.
- Include 4-6 dialogue lines with an `infographic` field.
- Make it educational but entertaining.
- Reply ONLY with valid JSON.

Return format:
{{
    "topic": "{topic}",
    "dialogues": [
        {{"character": "Peter", "text": "...", "infographic": "optional keyword"}},
        ...
    ]
}}
"""
