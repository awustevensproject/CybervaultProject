import bcrypt

ROUNDS = 12


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=ROUNDS)).decode()


def verify_password(password: str, stored: str) -> bool:
    if not stored:
        return False
    try:
        return bcrypt.checkpw(password.encode(), stored.encode())
    except ValueError:
        return False
