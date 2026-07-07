from flask import session


def start_session(user: dict) -> None:
    session.clear()
    session.permanent = True
    session["username"] = user["username"]
    session["user_id"] = user.get("id")
    session["role"] = user.get("role", "user")
