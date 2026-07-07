import json
import os
import time

MIN_INTERVAL_SEC = 2.0
MAX_PER_MINUTE = 10
WINDOW_SEC = 60

_STORE_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "rate_limit.json")


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
    cutoff = now - WINDOW_SEC
    return [t for t in times if t > cutoff]


def _check_key(data: dict[str, list[float]], key: str, now: float) -> tuple[bool, str | None]:
    recent = _prune(data.get(key, []), now)
    if recent and (now - recent[-1]) < MIN_INTERVAL_SEC:
        wait = MIN_INTERVAL_SEC - (now - recent[-1])
        return False, f"Slow down — wait {max(1, int(wait + 0.5))} second(s) and try again."
    if len(recent) >= MAX_PER_MINUTE:
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
    data = _load()
    now = time.time()

    for key in (f"{ip}:{action}", f"user:{action}:{subject.lower()}" if subject else None):
        if not key:
            continue
        allowed, message = _check_key(data, key, now)
        if not allowed:
            _save(data)
            return False, message

    _save(data)
    return True, None
