import asyncio
import logging
from contextlib import asynccontextmanager

import aio_pika
from aio_pika.exceptions import ConnectionClosed as RabbitConnectionClosed
from fastapi import FastAPI
from redis import RedisError
from redis import asyncio as redis
from redis.asyncio.connection import ConnectionPool

from app.config import get_settings
from app.travel_together.handlers import router as travel_router
from app.users.auth.handlers import router as auth_router
from app.users.user_profile.handlers import router as user_router

app = FastAPI()

app.include_router(travel_router)
app.include_router(user_router)
app.include_router(auth_router)


logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    retries = 3
    delay = 2
    redis_instance = None
    rabbit_connection = None

    for attempt in range(retries):
        try:
            logger.info("Attempt to connect Redis...")
            pool_conn = ConnectionPool.from_url(url=settings.REDIS_URL)
            r = redis.Redis(connection_pool=pool_conn)
            await r.ping()
            app.state.redis = redis_instance
            logger.info("Successfully connected to Redis and initialized cache")
            break
        except RedisError as e:
            logger.error(
                f"Redis connection attempt {attempt + 1}/{retries} failed: {str(e)}"
            )
            if attempt == retries - 1:
                raise RuntimeError(
                    "Failed to connect to Redis after multiple attempts"
                ) from e
            await asyncio.sleep(delay)

    for attempt in range(retries):
        try:
            logger.info("Attempt to connect RabbitMQ...")
            await aio_pika.connect_robust(settings.RABBITMQ_URL)
            logger.info("Successfully connected to RabbitMQ")
            break
        except RabbitConnectionClosed as e:
            logger.error(
                f"RabbitMQ connection attempt {attempt + 1}/{retries} failed: {str(e)}"
            )
            if attempt == retries - 1:
                raise RuntimeError(
                    "Failed to connect to RabbitMQ after multiple attempts"
                ) from e
            await asyncio.sleep(delay)
        yield

        # --- SHUTDOWN ---
        logger.info("Shutting down resources...")
        if rabbit_connection:
            await rabbit_connection.close()
            logger.info("RabbitMQ connection closed")

        if redis_instance:
            await redis_instance.aclose()
            logger.info("Redis connection closed")
