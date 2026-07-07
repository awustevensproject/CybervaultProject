import json
import os
import time

_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "rate_limit.json")
_WINDOW_SEC = 60

_LIMITS = {
    "login": (2.0, 10),
    "signup": (2.0, 10),
    "password_strength": (0.12, 120),
}


def _load() -> dict[str, list[float]]:
    try:
        with open(_STORE_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return {k: [float(t) for t in v] for k, v in data.items()}
    except (FileNotFoundError, json.JSONDecodeError, TypeError, ValueError):
        return {}


def _save(data: dict[str, list[float]]) -> None:
    os.makedirs(os.path.dirname(_STORE_PATH), exist_ok=True)
    with open(_STORE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


def _prune(times: list[float], now: float) -> list[float]:
    return [t for t in times if t > now - _WINDOW_SEC]


def _check_key(
    data: dict[str, list[float]],
    key: str,
    now: float,
    *,
    min_interval: float,
    max_per_minute: int,
) -> tuple[bool, str | None]:
    recent = _prune(data.get(key, []), now)
    if recent and (now - recent[-1]) < min_interval:
        wait = min_interval - (now - recent[-1])
        return False, f"Slow down — wait {max(1, int(wait + 0.5))} second(s) and try again."
    if len(recent) >= max_per_minute:
        return False, "Too many attempts this minute. Wait 60 seconds and try again."
    recent.append(now)
    data[key] = recent
    return True, None


def check_rate_limit(
    ip: str | None,
    action: str,
    *,
    subject: str | None = None,
) -> tuple[bool, str | None]:
    ip = ip or "unknown"
    min_interval, max_per_minute = _LIMITS.get(action, _LIMITS["login"])
    data = _load()
    now = time.time()

    keys = [f"{ip}:{action}"]
    if subject:
        keys.append(f"user:{action}:{subject.lower()}")

    for key in keys:
        allowed, message = _check_key(
            data,
            key,
            now,
            min_interval=min_interval,
            max_per_minute=max_per_minute,
        )
        if not allowed:
            _save(data)
            return False, message

    _save(data)
    return True, None
