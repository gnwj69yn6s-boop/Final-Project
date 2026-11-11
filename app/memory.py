from .db import sb


def load(user_id: str, limit: int = 30) -> list[dict]:
    res = (
        sb.table("memories").select("kind,content")
        .eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
    )
    return res.data


def save(user_id: str, kind: str, content: str) -> None:
    existing = (
        sb.table("memories").select("id")
        .eq("user_id", user_id).eq("content", content).execute().data
    )
    if not existing:
        sb.table("memories").insert(
            {"user_id": user_id, "kind": kind, "content": content}
        ).execute()


def as_prompt_block(user_id: str) -> str:
    items = load(user_id)
    if not items:
        return "(저장된 개인 정보 없음)"
    return "\n".join(f"- [{m['kind']}] {m['content']}" for m in items)
