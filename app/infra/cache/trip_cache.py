import json
import uuid
from typing import List, Optional

from redis import asyncio as Redis

from app.travel_together.schemas.trip import TripResponse


class TripCache:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def set_trip_cache(self, trip: TripResponse, trip_id: uuid.UUID):
        cache_key = f"trip:{trip_id}"
        trip_json = trip.model_dump_json()

        await self.redis.set(cache_key, trip_json, ex=3600)

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
