import os
from datetime import datetime, timezone

LOG_PATH = os.path.join(os.path.dirname(__file__), "..", "logs", "security.log")


def log_event(
    event_type: str,
    username: str | None = None,
    ip: str | None = None,
    details: str = "",
    user_id: str | None = None,
):
    os.makedirs(os.path.dirname(LOG_PATH), exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    line = f"{timestamp} | {event_type} | user={username or 'unknown'} | ip={ip or 'unknown'}"
    if user_id:
        line += f" | id={user_id}"
    if details:
        line += f" | {details}"
    with open(LOG_PATH, "a", encoding="utf-8") as f:
        f.write(line + "\n")
