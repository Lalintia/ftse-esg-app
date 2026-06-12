"""Rate limiter singleton shared across routers."""

from slowapi import Limiter
from slowapi.util import get_remote_address


def _client_ip(request) -> str:  # type: ignore[type-arg]
    # nginx sets X-Forwarded-For; use the leftmost (real client) IP
    fwd = request.headers.get("X-Forwarded-For", "")
    return fwd.split(",")[0].strip() or get_remote_address(request)


limiter = Limiter(key_func=_client_ip)
