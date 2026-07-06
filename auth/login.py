from utils.hashing import simple_hash
from database.users import get_user

def login_user(username, password):
    """
    Day 1: This is a MOCK authentication function.
    We are NOT validating real credentials yet.
    """

    user = get_user(username)

    if not user:
        return False

    # TODO (Day 2): Replace with proper hash comparison
    hashed_input = simple_hash(password)

    if hashed_input == user["password"]:
        return True

    return False