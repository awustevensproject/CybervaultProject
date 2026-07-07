import os

from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-change-me-before-production")
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "").lower() in ("1", "true", "yes")
SESSION_COOKIE_SECURE = os.environ.get("SESSION_COOKIE_SECURE", "").lower() in ("1", "true", "yes")


def database_configured() -> bool:
    return bool(SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY)
