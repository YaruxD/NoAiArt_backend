import asyncio
import aio_pika
import json
from neo4j import GraphDatabase
from ..settings import settings


class RBC_FOLLOW_AUTH:
    def __init__(self, amqp_url: str = settings.RBC_FOLLOW_AUTH_URL, queue_name: str = "user_add_follow"):
        self.amqp_url = amqp_url
        self.queue_name = queue_name
        self.connection: aio_pika.RobustConnection | None = None
        self.channel: aio_pika.abc.AbstractChannel | None = None
        self.queue: aio_pika.abc.AbstractQueue | None = None
        self.driver = GraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )
        print(f"Neo4j driver initialized for {settings.NEO4J_URI}")

    async def connect(self):
        """Подключение к RabbitMQ"""
        print(f"Connecting to RabbitMQ at {self.amqp_url}")
        self.connection = await aio_pika.connect_robust(self.amqp_url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
        print(f"Connected to queue: {self.queue_name}")

    def create_user(self, user_id: int, username: str):
        """Создание пользователя в Neo4j"""
        try:
            with self.driver.session() as session:
                session.run(
                    """
                    MERGE (u:User {id: $id})
                    SET u.username = $username
                    """,
                    id=user_id,
                    username=username
                )
            print(f" User {username} (id: {user_id}) added to follow graph")
        except Exception as e:
            print(f" Neo4j error: {e}")
            import traceback
            traceback.print_exc()

    async def on_message(self, message: aio_pika.abc.AbstractIncomingMessage):
        """Обработка входящего сообщения"""
        async with message.process():
            try:
                data = json.loads(message.body.decode())
                print(f"📨 Received: {data}")
                
                user_id = data.get("id")
                username = data.get("username")
                
                if user_id is not None and username is not None:
                    self.create_user(user_id, username)
                else:
                    print(f"Missing id or username in message: {data}")

            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
            except Exception as e:
                print(f"Consumer error: {e}")
                import traceback
                traceback.print_exc()

    async def start_consume(self):
        """Запуск чтения из очереди"""
        try:
            if not self.connection or not self.queue:
                await self.connect()

            await self.queue.consume(self.on_message)
            print(f"✅ Follow consumer started for queue: {self.queue_name}")
            print("⏳ Waiting for messages...\n")

            # Держим процесс живым
            await asyncio.Future()
        except asyncio.CancelledError:
            print("\n Consumer stopped")
        except Exception as e:
            print(f"Fatal error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await self.close()

    async def close(self):
        """Закрытие соединений"""
        if self.connection:
            await self.connection.close()
            print("🔌 RabbitMQ connection closed")
        
        if self.driver:
            self.driver.close()
            print("🔌 Neo4j driver closed")


RBCFollowAuth = RBC_FOLLOW_AUTH()