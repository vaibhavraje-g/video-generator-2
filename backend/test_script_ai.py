import httpx
import json

prompt = """
You are a viral TikTok/Reels scriptwriter using Family Guy style characters.
Generate a PUNCHY, HIGH-RETENTION script for a short video about "Quantum Superposition and Schrodinger's Cat".

Characters:
- Peter: Lovably dumb, funny misconceptions
- Stewie: Sarcastic condescending genius
- Brian: Dry intellectual humor

Return ONLY valid JSON matching this schema:
{
  "topic": "Quantum Superposition",
  "dialogues": [
    {"character": "Peter", "text": "...", "infographic": "...", "mood_descriptor": "excited"},
    {"character": "Stewie", "text": "...", "infographic": "...", "mood_descriptor": "sarcastic"},
    {"character": "Brian", "text": "...", "infographic": "...", "mood_descriptor": "intellectual"}
  ]
}
"""

r = httpx.post(
    "https://text.pollinations.ai/openai/chat/completions",
    json={
        "model": "openai",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
    },
    timeout=30.0
)

print("STATUS:", r.status_code)
if r.status_code == 200:
    content = r.json()["choices"][0]["message"]["content"]
    print("CONTENT:\n", content)
else:
    print("FAILED:", r.text)
