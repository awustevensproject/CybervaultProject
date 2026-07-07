from config import database_configured
from utils.hashing import hash_password

_fake_users = {
    "admin": {
        "username": "admin",
        "email": "admin@cybervault.local",
        "password": hash_password("Admin1234"),
        "role": "admin",
    },
    "student": {
        "username": "student",
        "email": "student@cybervault.local",
        "password": hash_password("Student123"),
        "role": "user",
    },
}


def _from_db(username: str) -> dict | None:
    from database.table_users import get_user_by_username

    user = get_user_by_username(username)
    if user and "password_hash" in user:
        user = {**user, "password": user["password_hash"]}
    return user


def get_user(username: str) -> dict | None:
    if database_configured():
        return _from_db(username)
    return _fake_users.get(username)


def username_exists(username: str) -> bool:
    if database_configured():
        from database.table_users import username_exists as exists

        return exists(username)
    return username.lower() in {k.lower() for k in _fake_users}


def email_exists(email: str) -> bool:
    email = email.lower().strip()
    if database_configured():
        from database.table_users import email_exists as exists

        return exists(email)
    return any(u["email"] == email for u in _fake_users.values())


def create_user(username: str, email: str, password: str, role: str = "user") -> dict:
    username = username.strip()
    email = email.lower().strip()

    if username_exists(username):
        raise ValueError("username_taken")
    if email_exists(email):
        raise ValueError("email_taken")

    hashed = hash_password(password)
    if database_configured():
        from database.table_users import create_user as db_create

        return db_create(username, email, hashed, role=role)

    user = {"username": username, "email": email, "password": hashed, "role": role}
    _fake_users[username] = user
    return user
