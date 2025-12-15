from redis import asyncio as redis

from app.config import Settings

settings = Settings()


def get_redis_connection() -> redis.Redis:
    return redis.Redis(
        host=settings.CACHE_HOST, db=settings.CACHE_DB, port=settings.CACHE_PORT
    )
