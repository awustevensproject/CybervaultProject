import re

MAX_PASSWORD_LEN = 128


def password_issues(password: str) -> list[str]:
    issues = []
    if len(password) < 10:
        issues.append("too_short")
    if len(password) > MAX_PASSWORD_LEN:
        issues.append("too_long")
    if not re.search(r"[a-z]", password):
        issues.append("no_lowercase")
    if not re.search(r"[A-Z]", password):
        issues.append("no_uppercase")
    if not re.search(r"\d", password):
        issues.append("no_digit")
    return issues


def is_strong_password(password: str) -> bool:
    return not password_issues(password)
