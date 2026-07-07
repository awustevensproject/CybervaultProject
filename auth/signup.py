import re

from database.users import create_user, email_exists, username_exists
from utils.hibp import is_breached
from utils.password_policy import is_strong_password
from utils.security_log import log_event

USERNAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]{3,20}$")
EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
MAX_EMAIL_LEN = 254


def register_user(username: str, email: str, password: str, ip: str | None = None) -> dict:
    if not USERNAME_PATTERN.match(username):
        log_event("signup_failure", username=username, ip=ip, details="rejected")
        raise ValueError("invalid_username")

    email = email.strip()
    if len(email) > MAX_EMAIL_LEN or not EMAIL_PATTERN.match(email):
        log_event("signup_failure", username=username, ip=ip, details="rejected")
        raise ValueError("invalid_email")

    if not is_strong_password(password):
        log_event("signup_failure", username=username, ip=ip, details="rejected")
        raise ValueError("weak_password")

    if is_breached(password):
        log_event("signup_failure", username=username, ip=ip, details="breached_password")
        raise ValueError("password_breached")

    if username_exists(username):
        log_event("signup_failure", username=username, ip=ip, details="rejected")
        raise ValueError("username_taken")

    if email_exists(email):
        log_event("signup_failure", username=username, ip=ip, details="rejected")
        raise ValueError("email_taken")

    try:
        user = create_user(username, email, password)
    except ValueError:
        raise
    except Exception:
        log_event("signup_failure", username=username, ip=ip, details="rejected")
        raise ValueError("signup_failed")

    log_event("signup_success", username=user["username"], ip=ip, user_id=user.get("id"))
    return user
