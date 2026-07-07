import re

from zxcvbn import zxcvbn

MAX_PASSWORD_LEN = 128
ZXCVBN_MIN_SCORE = 3
ZXCVBN_MAX_LEN = 72

STRENGTH_LABELS = {
    0: "Too guessable",
    1: "Very guessable",
    2: "Somewhat guessable",
    3: "Safely unguessable",
    4: "Very unguessable",
}

STRENGTH_COLORS = {
    0: "#ff3b30",
    1: "#ff3b30",
    2: "#ff9500",
    3: "#ffcc00",
    4: "#34c759",
}

STRENGTH_WIDTHS = {
    0: "20%",
    1: "40%",
    2: "60%",
    3: "80%",
    4: "100%",
}


def _zxcvbn_result(password: str) -> dict:
    return zxcvbn((password or "")[:ZXCVBN_MAX_LEN])


def analyze_password(password: str) -> dict:
    result = _zxcvbn_result(password)
    score = result["score"]
    crack_times = result.get("crack_times_display") or {}
    return {
        "score": score,
        "label": STRENGTH_LABELS.get(score, "Unknown"),
        "color": STRENGTH_COLORS.get(score, "#98989d"),
        "width": STRENGTH_WIDTHS.get(score, "0%"),
        "crack_time": crack_times.get("offline_slow_hashing_1e4_per_second", ""),
        "strong_enough": score >= ZXCVBN_MIN_SCORE,
    }


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
    if password and _zxcvbn_result(password)["score"] < ZXCVBN_MIN_SCORE:
        issues.append("zxcvbn_weak")
    return issues


def is_strong_password(password: str) -> bool:
    return not password_issues(password)
