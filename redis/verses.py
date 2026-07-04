import redis
from typing import Optional, Dict

class VerseRedis:
    def __init__(self, client: redis.Redis):
        self.r = client

    def key(self, uuid: str) -> str:
        return f"verse:{uuid}"

    def save(self, uuid: str, data: Dict):
        self.r.hset(self.key(uuid), mapping=data)

    def get(self, uuid: str) -> Optional[dict]:
        data = self.r.hgetall(self.key(uuid))
        if not data:
            return None
        return {k.decode(): v.decode() for k, v in data.items()}

    def delete(self, uuid: str):
        self.r.delete(self.key(uuid))

    def exists(self, uuid: str) -> bool:
        return self.r.exists(self.key(uuid)) == 1
