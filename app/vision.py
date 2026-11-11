import base64
import json
import re
import anthropic
from .config import ANTHROPIC_API_KEY, CLAUDE_MODEL

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

PROMPT = """이 사진은 냉장고 또는 식재료 사진입니다.
보이는 식재료만 추출해 아래 JSON 배열로만 답하세요. 다른 설명은 금지합니다.
확실하지 않은 것은 confidence를 "low"로 표시하고, 보이지 않는 것은 추측하지 마세요.
[{"name": "재료명(한국어)", "amount": "대략적 양 또는 빈 문자열", "confidence": "high|low"}]"""


def analyze_fridge(image_bytes: bytes, media_type: str) -> list[dict]:
    b64 = base64.standard_b64encode(image_bytes).decode()
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=1000,
        messages=[{
            "role": "user",
            "content": [
                {"type": "image",
                 "source": {"type": "base64", "media_type": media_type, "data": b64}},
                {"type": "text", "text": PROMPT},
            ],
        }],
    )
    text = resp.content[0].text
    match = re.search(r"\[.*\]", text, re.S)
    try:
        return json.loads(match.group(0)) if match else []
    except json.JSONDecodeError:
        return []
