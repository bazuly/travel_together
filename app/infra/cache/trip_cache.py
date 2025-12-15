import json
import uuid
from typing import List, Optional

from redis import asyncio as Redis

from app.travel_together.schemas.trip import TripResponse


class TripCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set_trip_cache(self, trip: TripResponse, trip_id: uuid.UUID):
        # Используем trip_id для уникального ключа
        cache_key = f"trip:{trip_id}"

        # 1. Сериализуем один объект в JSON-строку. Используем .model_dump() для Pydantic v2
        trip_json = trip.model_dump_json()

        # 2. Кэшируем строку, например, с помощью SET
        await self.redis.set(cache_key, trip_json)

    async def get_trip_from_cache(
        self, trip_id: uuid.UUID
    ) -> Optional[List[TripResponse]]:
        cache_key = f"trip:{trip_id}"
        trip_json = await self.redis.get(cache_key)

        if trip_json:
            try:
                # Десериализуем обратно в модель
                return TripResponse.model_validate_json(trip_json)
            except json.JSONDecodeError as e:
                raise ValueError("Invalid trip data in Redis") from e
        return None
