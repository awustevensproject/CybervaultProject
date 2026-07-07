from utils.hashing import simple_hash
from database.users import get_user_by_email
from utils.security_log import log_event


def login_user(email: str, password: str, ip: str | None = None) -> dict | None:
    user = get_user_by_email(email)

    if not user:
        log_event("login_failure", username=email, ip=ip, details="user_not_found")
        return None

    hashed_input = simple_hash(password)

    if hashed_input != user["password"]:
        log_event("login_failure", username=user["username"], ip=ip, details="invalid_password")
        return None

    log_event("login_success", username=user["username"], ip=ip)
    return user
