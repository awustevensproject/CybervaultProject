from database.users import get_user
from utils.hashing import verify_password
from utils.security_log import log_event


def login_user(username: str, password: str, ip: str | None = None) -> dict | None:
    user = get_user(username)
    ok = user and verify_password(password, user.get("password", ""))

    if not ok:
        log_event("login_failure", username=username or None, ip=ip, details="invalid_credentials")
        return None

    log_event(
        "login_success",
        username=user["username"],
        ip=ip,
        user_id=user.get("id"),
    )
    return {
        "id": user.get("id"),
        "username": user["username"],
        "email": user.get("email"),
        "role": user.get("role", "user"),
    }
