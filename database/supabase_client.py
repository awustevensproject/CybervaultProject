from supabase import Client, create_client

from config import SUPABASE_SERVICE_ROLE_KEY, SUPABASE_URL

_client: Client | None = None


def get_supabase_admin() -> Client:
    global _client
    if _client is None:
        if not SUPABASE_SERVICE_ROLE_KEY:
            raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY is required")
        _client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    return _client
