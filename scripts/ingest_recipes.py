"""data/recipes.csv → 임베딩 → Supabase 적재.
CSV 컬럼: title, ingredients(쉼표 구분), steps, time_min, difficulty(쉬움/보통/어려움)"""
import pandas as pd
from app.db import sb
from app.embed import embed

df = pd.read_csv("data/recipes.csv")
BATCH = 32
for i in range(0, len(df), BATCH):
    chunk = df.iloc[i:i + BATCH]
    texts = [f"{r.title}. 재료: {r.ingredients}. {r.steps}" for r in chunk.itertuples()]
    embs = embed(texts, "document")
    rows = [{
        "title": r.title,
        "ingredients": [x.strip() for x in r.ingredients.split(",")],
        "steps": r.steps,
        "time_min": int(r.time_min),
        "difficulty": r.difficulty,
        "embedding": e,
    } for r, e in zip(chunk.itertuples(), embs)]
    sb.table("recipes").insert(rows).execute()
    print(f"{i + len(chunk)}/{len(df)} 완료")
