import hashlib
import urllib.error
import urllib.request

HIBP_RANGE_URL = "https://api.pwnedpasswords.com/range/{prefix}"
USER_AGENT = "CyberVault-PasswordChecker/1.0"
TIMEOUT_SEC = 5


def pwned_count(password: str) -> int | None:
    """Return breach count via HIBP k-anonymity API, or None if the check failed."""
    digest = hashlib.sha1(password.encode("utf-8")).hexdigest().upper()
    prefix, suffix = digest[:5], digest[5:]
    request = urllib.request.Request(
        HIBP_RANGE_URL.format(prefix=prefix),
        headers={"User-Agent": USER_AGENT, "Add-Padding": "true"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SEC) as response:
            body = response.read().decode("utf-8")
    except (urllib.error.URLError, TimeoutError, OSError):
        return None

    for line in body.splitlines():
        if not line:
            continue
        found_suffix, count = line.split(":", 1)
        if found_suffix == suffix:
            return int(count)
    return 0


def is_breached(password: str, *, fail_closed: bool = False) -> bool:
    count = pwned_count(password)
    if count is None:
        return fail_closed
    return count > 0


def breach_issue(password: str) -> str | None:
    """Return signup error code if password fails breach policy."""
    count = pwned_count(password)
    if count is None:
        return "breach_check_failed"
    if count > 0:
        return "password_breached"
    return None
