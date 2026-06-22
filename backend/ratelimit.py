# backend/ratelimit.py
"""
In-memory sliding-window rate limiter.

Protects endpoints from rapid abuse (independent of monthly billing quotas).
Keyed by an arbitrary identifier (api key, ip, uid). For multi-instance
deployments this should be backed by Redis, but in-memory is sufficient for
a single Render instance and avoids extra infra.
"""
from __future__ import annotations
import time
import threading
from collections import deque, defaultdict

_lock = threading.Lock()
_hits: dict[str, deque] = defaultdict(deque)


def check(key: str, max_requests: int = 20, window_seconds: int = 60) -> bool:
    """Return True if the request is allowed, False if rate limited."""
    now = time.time()
    with _lock:
        q = _hits[key]
        # drop timestamps outside the window
        while q and q[0] <= now - window_seconds:
            q.popleft()
        if len(q) >= max_requests:
            return False
        q.append(now)
        return True
