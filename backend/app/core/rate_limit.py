import threading
import time
from collections import defaultdict, deque

from app.core.config import get_settings
from app.core.exceptions import TooManyRequests


class SlidingWindowLimiter:
    """Limiteur en mémoire par processus ; à remplacer par Redis en déploiement multi-instances."""

    def __init__(self) -> None:
        self._hits: dict[str, deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()

    def check(self, key: str, limit: int, window_seconds: int) -> None:
        if not get_settings().rate_limit_enabled:
            return
        now = time.monotonic()
        with self._lock:
            hits = self._hits[key]
            while hits and now - hits[0] > window_seconds:
                hits.popleft()
            if len(hits) >= limit:
                retry_after = max(1, int(window_seconds - (now - hits[0])))
                raise TooManyRequests("Trop de requêtes, réessayez plus tard", headers={"Retry-After": str(retry_after)})
            hits.append(now)

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


limiter = SlidingWindowLimiter()
