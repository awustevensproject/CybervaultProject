"""
In-memory user store (temporary — replace with Supabase in production).
"""

from utils.hashing import simple_hash

_users = {
    "admin": {
        "username": "admin",
        "email": "admin@cybervault.local",
        "password": simple_hash("admin123"),
        "role": "admin",
    },
    "student": {
        "username": "student",
        "email": "student@cybervault.local",
        "password": simple_hash("pass"),
        "role": "user",
    },
}


def get_user(username: str):
    return _users.get(username)


def get_user_by_email(email: str):
    email = email.lower().strip()
    for user in _users.values():
        if user["email"].lower() == email:
            return user
    return None


def username_exists(username: str) -> bool:
    return username.lower() in {k.lower() for k in _users}


def email_exists(email: str) -> bool:
    return get_user_by_email(email) is not None


def create_user(username: str, email: str, password: str) -> dict:
    username = username.strip()
    email = email.lower().strip()

    if username_exists(username):
        raise ValueError("username_taken")
    if email_exists(email):
        raise ValueError("email_taken")

    user = {
        "username": username,
        "email": email,
        "password": simple_hash(password),
        "role": "user",
    }
    _users[username] = user
    return user
