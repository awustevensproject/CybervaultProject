import re

from database.users import create_user
from utils.security_log import log_event

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")


def register_user(username: str, email: str, password: str, ip: str | None = None) -> dict:
    if not USERNAME_PATTERN.match(username):
        log_event("signup_failure", username=username, ip=ip, details="invalid_username")
        raise ValueError("invalid_username")

    if len(password) < 8:
        log_event("signup_failure", username=username, ip=ip, details="weak_password")
        raise ValueError("weak_password")

    try:
        user = create_user(username, email, password)
    except ValueError as exc:
        log_event("signup_failure", username=username, ip=ip, details=str(exc))
        raise

    log_event("signup_success", username=user["username"], ip=ip)
    return user
