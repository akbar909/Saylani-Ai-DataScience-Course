from datetime import datetime, timedelta
from threading import Lock
from typing import Any


class TTLCache:
    def __init__(self, ttl_seconds: int = 300) -> None:
        self.ttl_seconds = ttl_seconds
        self._store: dict[str, tuple[datetime, Any]] = {}
        self._lock = Lock()

    def get(self, key: str) -> Any | None:
        with self._lock:
            if key not in self._store:
                return None

            expiry, value = self._store[key]
            if datetime.utcnow() > expiry:
                del self._store[key]
                return None

            return value

    def set(self, key: str, value: Any) -> None:
        with self._lock:
            expiry = datetime.utcnow() + timedelta(seconds=self.ttl_seconds)
            self._store[key] = (expiry, value)

    def invalidate_prefix(self, prefix: str) -> None:
        with self._lock:
            keys = [k for k in self._store if k.startswith(prefix)]
            for key in keys:
                del self._store[key]
