import secrets

from flask import session


def get_csrf_token() -> str:
    token = session.get("_csrf")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf"] = token
    return token


def validate_csrf_token(token: str | None) -> bool:
    expected = session.get("_csrf")
    if not expected or not token:
        return False
    return secrets.compare_digest(expected, token)
