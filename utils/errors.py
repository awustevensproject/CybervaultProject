AUTH_ERRORS = {
    "table_missing": "Database not set up — run supabase/users_table.sql in Supabase SQL Editor first.",
    "bad_credentials": "Invalid Supabase key — check SUPABASE_SERVICE_ROLE_KEY in your .env file.",
    "database_error": "Database error. Check your Supabase connection and try again.",
    "invalid_credentials": "Invalid username or password.",
}

SIGNUP_ERRORS = {
    **AUTH_ERRORS,
    "username_taken": "That username is already taken.",
    "email_taken": "An account with that email already exists.",
    "invalid_username": "Username must be 3–20 characters (letters, numbers, _).",
    "weak_password": "Password is too weak — at least 10 characters, upper, lower, number, and a zxcvbn score of 3+.",
    "password_breached": "That password has appeared in a data breach. Please choose a different one.",
    "invalid_email": "Please enter a valid email address (e.g. you@gmail.com).",
    "signup_failed": "Could not create account. Please try again.",
}


def message_for(code: str, *, signup: bool = False) -> str | None:
    table = SIGNUP_ERRORS if signup else AUTH_ERRORS
    return table.get(code)
