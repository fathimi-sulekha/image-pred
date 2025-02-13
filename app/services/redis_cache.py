import redis
import json
from app.core.config import settings

class RedisCache:
    def __init__(self):
        self.client = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)

    async def get_cache(self, key: str):
        """Get cached result from Redis."""
        data = self.client.get(key)
        return json.loads(data) if data else None

    async def set_cache(self, key: str, value: dict, ttl: int = 3600):
        """Set a new cache entry with TTL (default 1 hour)."""
        self.client.setex(key, ttl, json.dumps(value))
