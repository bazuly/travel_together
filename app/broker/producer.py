import json

import aio_pika

from app.config import get_settings

settings = get_settings()


class TripTaskProducer:
    def __init__(self):
        self._connection = None

    async def get_connection(self) -> aio_pika.Connection:
        if self._connection is None or self._connection.is_closed:
            self._connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
        return self._connection

    async def send_to_pdf_worker(self, trip_data: dict):
        connection = await self.get_connection()

        async with connection.channel() as channel:
            # объявляем очередь
            # флаг durable означает, что очередь не потеряется
            # если сервер упадет
            await channel.declare_queue("pdf_generation", durable=True)

            message_body = json.dumps(trip_data).encode()

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=message_body,
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                ),
                routing_key="pdf_generation",
            )
