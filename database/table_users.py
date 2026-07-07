from postgrest.exceptions import APIError

from database.supabase_client import get_supabase_admin


def _handle_db_error(exc: Exception) -> None:
    if isinstance(exc, APIError):
        code = getattr(exc, "code", None)
        text = str(exc)
        if code == "PGRST205" or "Could not find the table" in text:
            raise ValueError("table_missing") from exc
        if code in ("PGRST301", "42501") or "JWT" in text or "Invalid API key" in text:
            raise ValueError("bad_credentials") from exc
    raise ValueError("database_error") from exc


def _users():
    return get_supabase_admin().table("users")


def get_user_by_username(username: str) -> dict | None:
    try:
        result = (
            _users()
            .select("id, username, email, password_hash, role")
            .eq("username", username)
            .limit(1)
            .execute()
        )
    except Exception as exc:
        _handle_db_error(exc)
    return result.data[0] if result.data else None


def username_exists(username: str) -> bool:
    try:
        result = _users().select("id").eq("username", username).limit(1).execute()
    except Exception as exc:
        _handle_db_error(exc)
    return bool(result.data)


def email_exists(email: str) -> bool:
    try:
        result = _users().select("id").eq("email", email.lower().strip()).limit(1).execute()
    except Exception as exc:
        _handle_db_error(exc)
    return bool(result.data)


def create_user(username: str, email: str, password_hash: str, role: str = "user") -> dict:
    row = {
        "username": username.strip(),
        "email": email.lower().strip(),
        "password_hash": password_hash,
        "role": role,
    }
    try:
        result = _users().insert(row).execute()
    except Exception as exc:
        _handle_db_error(exc)
    if not result.data:
        raise ValueError("insert_failed")
    user = result.data[0]
    return {
        "id": user["id"],
        "username": user["username"],
        "email": user["email"],
        "role": user.get("role", "user"),
    }
