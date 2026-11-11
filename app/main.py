from datetime import datetime, timezone, timedelta
from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from .config import DAILY_LIMIT, INTERNAL_API_KEY
from .db import sb
from . import agent, memory, vision

app = FastAPI(title="FridgeMate")

ALLOWED = {"image/jpeg", "image/png", "image/webp"}
MAX_BYTES = 5 * 1024 * 1024


class UserIn(BaseModel):
    nickname: str
    consent: bool
    notify_email: str | None = None


class ChatIn(BaseModel):
    user_id: str
    message: str
    ingredients: list[str] = []


class FeedbackIn(BaseModel):
    user_id: str
    rating: int
    comment: str | None = None


@app.get("/health")
def health():
    return {"ok": True}


@app.post("/api/users")
def create_user(body: UserIn):
    if not body.consent:
        raise HTTPException(400, "개인정보 수집 동의가 필요합니다.")
    row = sb.table("users").insert({
        "nickname": body.nickname.strip()[:30],
        "notify_email": body.notify_email,
        "consent_at": datetime.now(timezone.utc).isoformat(),
    }).execute().data[0]
    return {"user_id": row["id"]}


@app.post("/api/fridge")
async def fridge(file: UploadFile = File(...)):
    if file.content_type not in ALLOWED:
        raise HTTPException(400, "jpg/png/webp 이미지만 지원합니다.")
    data = await file.read()
    if len(data) > MAX_BYTES:
        raise HTTPException(413, "이미지는 5MB 이하여야 합니다.")
    # 이미지는 저장하지 않고 분석 후 폐기한다.
    return {"ingredients": vision.analyze_fridge(data, file.content_type)}


def _check_limit(user_id: str):
    since = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    cnt = (
        sb.table("messages").select("id", count="exact")
        .eq("user_id", user_id).eq("role", "user").gte("created_at", since).execute().count
    )
    if cnt >= DAILY_LIMIT:
        raise HTTPException(429, "오늘 사용 한도에 도달했어요. 내일 다시 이용해 주세요.")


@app.post("/api/chat")
def chat(body: ChatIn):
    _check_limit(body.user_id)
    answer = agent.chat(body.user_id, body.message[:1000], body.ingredients)
    return {"answer": answer, "ai_generated": True}


@app.get("/api/memory/{user_id}")
def get_memory(user_id: str):
    return {"memories": memory.load(user_id)}


@app.get("/api/shopping/{user_id}")
def shopping(user_id: str):
    rows = sb.table("shopping_items").select("item,done").eq("user_id", user_id).execute().data
    return {"items": rows}


@app.post("/api/feedback")
def feedback(body: FeedbackIn):
    if body.rating not in (-1, 1):
        raise HTTPException(400, "rating은 -1 또는 1입니다.")
    sb.table("feedback").insert(body.model_dump()).execute()
    return {"ok": True}


@app.delete("/api/users/{user_id}")
def delete_user(user_id: str):
    sb.table("users").delete().eq("id", user_id).execute()  # on delete cascade
    return {"deleted": True}


@app.get("/api/internal/digests")
def digests(x_api_key: str = Header(default="")):
    """n8n 전용. 이메일 수신 동의자에게 보낼 개인화 메시지를 생성한다."""
    if x_api_key != INTERNAL_API_KEY:
        raise HTTPException(401, "unauthorized")
    users = sb.table("users").select("id,nickname,notify_email").not_.is_("notify_email", "null").execute().data
    out = []
    for u in users:
        items = [
            r["item"] for r in sb.table("shopping_items").select("item")
            .eq("user_id", u["id"]).eq("done", False).execute().data
        ]
        msg = agent.weekly_digest_text(u["nickname"], memory.as_prompt_block(u["id"]), items)
        out.append({"email": u["notify_email"], "nickname": u["nickname"], "message": msg})
    return {"digests": out}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
