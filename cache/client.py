import redis

from config import Config

# NOTE: this package is named `cache`, not `redis`. The original project
# had a local `redis/` folder that shadowed the real `redis` pip package,
# which broke every import of the actual library. Keep it named `cache`.

_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """Return a process-wide Redis client, created lazily."""
    global _redis_client

    if _redis_client is None:
        _redis_client = redis.Redis.from_url(
            Config.REDIS_URL,
            decode_responses=True,
        )

    return _redis_client
