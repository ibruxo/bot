from redis import Redis


class RateLimiter:
    """
    Simple fixed-window rate limiter backed by Redis INCR + EXPIRE.

    Not perfectly precise at window boundaries (a classic fixed-window
    trade-off), but it's cheap, has no extra dependencies, and is more
    than enough to stop a chat from spamming /random.
    """

    def __init__(self, redis_client: Redis, max_requests: int, window_seconds: int):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def _key(self, identifier: str) -> str:
        return f"ratelimit:{identifier}"

    def allow(self, identifier: str) -> bool:
        """Return True if `identifier` (e.g. a chat_id) may act now."""
        key = self._key(identifier)

        count = self.redis.incr(key)

        if count == 1:
            # First hit in this window: start the countdown.
            self.redis.expire(key, self.window_seconds)

        return count <= self.max_requests

    def remaining_seconds(self, identifier: str) -> int:
        ttl = self.redis.ttl(self._key(identifier))
        return max(ttl, 0)
