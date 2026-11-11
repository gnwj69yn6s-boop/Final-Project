from supabase import create_client
from .config import SUPABASE_URL, SUPABASE_SERVICE_KEY

sb = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
