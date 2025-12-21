import asyncio
import json
import logging
import os

import aio_pika
from fpdf import FPDF

from app.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


def generate_pdf(data):
    # создаем директории внутри контейнера
    # и сетапим имена для наших pdf-поездок
    os.makedirs(settings.PDF_DIR, exist_ok=True)
    filename = f"trip_{data['trip_id']}.pdf"

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"Trip Ticket: {data['title']}", ln=True, align="C")
    pdf.cell(200, 10, txt=f"Destination: {data['destination']}", ln=True)
    pdf.cell(200, 10, txt=f"Date: {data['start_date']}", ln=True)

    filepath = os.path.join(settings.PDF_DIR, filename)
    pdf.output(filepath)

    # TODO: для сохранения в БД, если потребуется
    relative_path = os.path.join("trip_pdfs", filename)
    return relative_path


async def on_message(message: aio_pika.IncomingMessage):
    async with message.process():
        data = json.loads(message.body.decode())
        logger.info(f"Generating PDF for trip: {data['title']}")

        # Вызываем тяжелую функцию (лучше в потоке, если она блокирующая)
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, generate_pdf, data)

        logger.info("PDF done!")


async def main():
    connection = await aio_pika.connect_robust(settings.RABBITMQ_URL)
    try:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue("pdf_generation", durable=True)
        await queue.consume(on_message)

        logger.info("Worker started and ready for tasks.")
        await asyncio.Future()
    finally:
        await connection.close()


if __name__ == "__main__":
    asyncio.run(main())
