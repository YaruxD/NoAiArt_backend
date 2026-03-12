import asyncio
import aio_pika
import json
from ..settings import settings


async def send_message_to_followservice(user_data: dict):
    connection = await aio_pika.connect_robust(
        settings.RBP_FOLLOW_AUTH_URL  # имя контейнера, не localhost
    )

    async with connection:
        channel = await connection.channel()
        queue = await channel.declare_queue("user_add_follow", durable=True)

        await channel.default_exchange.publish(
            aio_pika.Message(body=json.dumps(user_data).encode()),
            routing_key=queue.name,
        )



