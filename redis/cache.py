from redis.client import redis_client


class Cache:
    @staticmethod
    def set(key: str, value: str, ttl: int = 3600):
        redis_client.setex(key, ttl, value)

    @staticmethod
    def get(key: str):
        return redis_client.get(key)
