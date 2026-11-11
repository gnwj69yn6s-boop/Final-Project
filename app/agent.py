import json
import anthropic
from .config import ANTHROPIC_API_KEY, CLAUDE_MODEL
from .db import sb
from . import rag, memory

client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

SYSTEM_TEMPLATE = """당신은 'FridgeMate', 친절한 한국어 요리 코치입니다.

## 사용자 개인 정보 (장기 기억)
{memory_block}

## 사용자가 확정한 현재 재료
{ingredients}

## 규칙 (반드시 준수)
1. 레시피를 추천할 때는 반드시 search_recipes 도구로 검색한 결과만 근거로 삼으세요.
   검색 결과에 없는 레시피를 지어내지 마세요. 적합한 결과가 없으면 솔직히 말하세요.
2. [allergy] 정보에 해당하는 재료가 포함된 레시피는 절대 추천하지 마세요.
   [dislike]는 가급적 피하고, [skill] 수준에 맞는 난이도를 고르세요.
3. 대화에서 새로운 알레르기, 비선호, 식단, 조리 수준이 드러나면 save_memory로 저장하세요.
   (예: "나 새우 알러지야" → kind=allergy, content="새우")
4. 추천 레시피에 부족한 재료가 있고 사용자가 원하면 add_to_shopping_list로 저장하세요.
5. 답변은 3~6문장 + 필요 시 단계 목록으로 간결하게, 이모지는 최소로 사용하세요.
6. 알레르기가 있는 사용자에게는 마지막에 "성분은 직접 한 번 더 확인해 주세요"를 덧붙이세요."""

TOOLS = [
    {
        "name": "search_recipes",
        "description": "레시피 DB에서 질의와 유사한 레시피를 검색한다. 재료와 조건을 자연어로 넣는다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "예: '계란, 대파로 만드는 간단한 요리'"},
                "max_time": {"type": "integer", "description": "최대 조리 시간(분). 선택"},
            },
            "required": ["query"],
        },
    },
    {
        "name": "save_memory",
        "description": "사용자의 알레르기/비선호/식단/조리 수준/기타 메모를 장기 기억에 저장한다.",
        "input_schema": {
            "type": "object",
            "properties": {
                "kind": {"type": "string", "enum": ["allergy", "dislike", "diet", "skill", "note"]},
                "content": {"type": "string"},
            },
            "required": ["kind", "content"],
        },
    },
    {
        "name": "add_to_shopping_list",
        "description": "사용자의 장보기 목록에 부족한 재료를 추가한다.",
        "input_schema": {
            "type": "object",
            "properties": {"items": {"type": "array", "items": {"type": "string"}}},
            "required": ["items"],
        },
    },
]


def _run_tool(name: str, args: dict, user_id: str):
    if name == "search_recipes":
        rows = rag.search_recipes(args["query"], args.get("max_time"))
        return [{k: r[k] for k in ("title", "ingredients", "steps", "time_min", "difficulty")} for r in rows]
    if name == "save_memory":
        memory.save(user_id, args["kind"], args["content"])
        return {"ok": True}
    if name == "add_to_shopping_list":
        rows = [{"user_id": user_id, "item": i} for i in args["items"]]
        if rows:
            sb.table("shopping_items").insert(rows).execute()
        return {"ok": True, "added": args["items"]}
    return {"error": f"unknown tool {name}"}


def _history(user_id: str, n: int = 10) -> list[dict]:
    rows = (
        sb.table("messages").select("role,content")
        .eq("user_id", user_id).order("id", desc=True).limit(n).execute().data
    )
    return list(reversed(rows))


def chat(user_id: str, user_message: str, ingredients: list[str]) -> str:
    system = SYSTEM_TEMPLATE.format(
        memory_block=memory.as_prompt_block(user_id),
        ingredients=", ".join(ingredients) if ingredients else "(미확정)",
    )
    messages = _history(user_id) + [{"role": "user", "content": user_message}]

    resp = client.messages.create(
        model=CLAUDE_MODEL, max_tokens=1500, system=system, tools=TOOLS, messages=messages
    )
    for _ in range(5):  # 도구 호출 무한 루프 방지
        if resp.stop_reason != "tool_use":
            break
        messages.append({"role": "assistant", "content": resp.content})
        results = []
        for block in resp.content:
            if block.type == "tool_use":
                out = _run_tool(block.name, block.input, user_id)
                results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": json.dumps(out, ensure_ascii=False),
                })
        messages.append({"role": "user", "content": results})
        resp = client.messages.create(
            model=CLAUDE_MODEL, max_tokens=1500, system=system, tools=TOOLS, messages=messages
        )

    answer = "".join(b.text for b in resp.content if b.type == "text").strip()
    sb.table("messages").insert([
        {"user_id": user_id, "role": "user", "content": user_message},
        {"user_id": user_id, "role": "assistant", "content": answer},
    ]).execute()
    return answer


def weekly_digest_text(nickname: str, memory_block: str, items: list[str]) -> str:
    resp = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=400,
        messages=[{"role": "user", "content": (
            f"{nickname}님에게 보낼 주간 장보기 알림 메시지를 4문장 이내로 작성하세요.\n"
            f"개인 정보:\n{memory_block}\n장보기 목록: {', '.join(items) or '없음'}\n"
            "목록이 없으면 냉장고 재료 점검을 권하는 가벼운 메시지로 쓰세요. "
            "마지막 줄에 '(AI가 생성한 메시지입니다)'를 붙이세요."
        )}],
    )
    return resp.content[0].text.strip()
