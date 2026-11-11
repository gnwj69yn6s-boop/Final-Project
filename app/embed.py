import voyageai
from .config import VOYAGE_API_KEY, EMBED_MODEL

_vo = voyageai.Client(api_key=VOYAGE_API_KEY)


def embed(texts: list[str], input_type: str = "document") -> list[list[float]]:
    return _vo.embed(texts, model=EMBED_MODEL, input_type=input_type).embeddings
