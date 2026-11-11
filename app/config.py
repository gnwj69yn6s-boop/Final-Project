import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL = os.environ["CLAUDE_MODEL"]
VOYAGE_API_KEY = os.environ["VOYAGE_API_KEY"]
EMBED_MODEL = os.getenv("EMBED_MODEL", "voyage-3-lite")
SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_SERVICE_KEY = os.environ["SUPABASE_SERVICE_KEY"]
INTERNAL_API_KEY = os.environ["INTERNAL_API_KEY"]
DAILY_LIMIT = int(os.getenv("DAILY_LIMIT", "30"))
