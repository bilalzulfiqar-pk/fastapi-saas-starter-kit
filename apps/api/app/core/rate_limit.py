from __future__ import annotations

import asyncio
import logging
from collections import defaultdict, deque
from dataclasses import dataclass
from time import time

from fastapi import Request
from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.core.config import get_settings
from app.core.errors import AppError

logger = logging.getLogger(__name__)


@dataclass
class RateLimitResult:
    allowed: bool
    remaining: int


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._store: dict[str, deque[float]] = defaultdict(deque)
        self._lock = asyncio.Lock()

    async def hit(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        async with self._lock:
            now = time()
            bucket = self._store[key]
            while bucket and bucket[0] <= now - window_seconds:
                bucket.popleft()
            if len(bucket) >= limit:
                return RateLimitResult(allowed=False, remaining=0)
            bucket.append(now)
            return RateLimitResult(allowed=True, remaining=max(limit - len(bucket), 0))


class RedisRateLimiter:
    def __init__(self, redis_url: str) -> None:
        self.client = Redis.from_url(redis_url, decode_responses=True)

    async def hit(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        async with self.client.pipeline(transaction=True) as pipe:
            now = int(time())
            window_key = f"rl:{key}:{now // window_seconds}"
            pipe.incr(window_key)
            pipe.expire(window_key, window_seconds)
            count, _ = await pipe.execute()
            count = int(count)
            return RateLimitResult(allowed=count <= limit, remaining=max(limit - count, 0))


_memory_backend = InMemoryRateLimiter()
_redis_backend: RedisRateLimiter | None = None


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    if request.client:
        return request.client.host
    return "unknown"


async def enforce_rate_limit(name: str, request: Request, limit: int, window_seconds: int, identifier: str) -> None:
    key = f"{name}:{_client_ip(request)}:{identifier.lower()}"
    global _redis_backend
    if _redis_backend is None:
        _redis_backend = RedisRateLimiter(get_settings().redis_url)

    try:
        result = await _redis_backend.hit(key, limit, window_seconds)
    except RedisError as exc:
        logger.warning("Falling back to in-memory rate limiter: %s", exc)
        result = await _memory_backend.hit(key, limit, window_seconds)

    if not result.allowed:
        raise AppError(code="rate_limited", message="Too many requests", status_code=429)

