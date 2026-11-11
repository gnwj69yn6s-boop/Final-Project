from .db import sb
from .embed import embed


def search_recipes(query: str, max_time: int | None = None, k: int = 4) -> list[dict]:
    """질의를 임베딩해 pgvector에서 유사 레시피 상위 k개를 반환한다."""
    q_emb = embed([query], "query")[0]
    res = sb.rpc(
        "match_recipes",
        {"query_embedding": q_emb, "match_count": k, "max_time": max_time},
    ).execute()
    return res.data
