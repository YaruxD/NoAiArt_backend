import asyncio
import aio_pika
import json
from ..settings import settings
from ..database import sessionmaker
from ..models import User

class RBC_USER_AUTH:
    def __init__(self, amqp_url: str = settings.RBC_USER_AUTH_URL, queue_name: str = "user_add"):
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None
        self.queue: aio_pika.abc.AbstractQueue | None = None

    async def connect(self):

        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)

    async def on_message(self, message: aio_pika.abc.AbstractIncomingMessage):

        async with message.process():
            try:
                data = json.loads(message.body.decode())

                user_id = data.get("id")
                username = data.get("username")
                name = data.get("name")
                new_user = User(
                    id = user_id,
                    username = username,
                    name = name
                )
                async with sessionmaker() as db:
                    db.add(new_user)
                    await db.commit()
                    await db.refresh(new_user)

            except Exception as e:
                print(e)

    async def start_consume(self):
        """Запуск чтения из очереди."""
        if not self.connection or not self.queue:
            await self.connect()

        await self.queue.consume(self.on_message)

        await asyncio.Future()  # держим процесс живым

    async def close(self):
        """Закрытие соединения с RabbitMQ."""
        if self.connection:
            await self.connection.close()


RBCUserAuth = RBC_USER_AUTH()