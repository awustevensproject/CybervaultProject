import os
from functools import wraps

from flask import redirect, request, session, url_for

from database.users import get_user
from utils.security_log import log_event


def client_ip() -> str:
    if os.environ.get("TRUST_PROXY") and request.headers.get("X-Forwarded-For"):
        return request.headers["X-Forwarded-For"].split(",")[0].strip()
    return request.remote_addr or "unknown"


def _deny(reason: str, username: str | None = None):
    log_event("access_denied", username=username, ip=client_ip(), details=reason)
    return redirect(url_for("login"))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("username"):
            return _deny(f"login_required:{request.path}")
        return view(*args, **kwargs)

    return wrapped


def role_required(role: str):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            username = session.get("username")
            if not username:
                return _deny(f"login_required:{request.path}")

            user = get_user(username)
            if not user or user.get("role") != role:
                log_event(
                    "access_denied",
                    username=username,
                    ip=client_ip(),
                    details=f"role_required:{role}:{request.path}",
                )
                return redirect(url_for("dashboard"))

            return view(*args, **kwargs)

        return wrapped

    return decorator
