from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import logging

from settings import settings



client = QdrantClient(f"{settings.QDRANT_URL}")

logger = logging.getLogger(__name__)

class QdrantMigrationManager:
    def __init__(self, client: QdrantClient):
        self.client = client
    
    def run_all_migrations(self):
        """Запуск всех миграций"""
        self._create_image_collection()
    
    def _create_image_collection(self):
        """Основная коллекция для изображений/пинов"""
        collection_name = "images"
        
        try:
            # Проверяем существование коллекции
            self.client.get_collection(collection_name)
            logger.info(f"Collection '{collection_name}' already exists")
            return
        except Exception:
            # Коллекция не существует, создаем
            pass
        
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=512,  # Размер вектора изображения (CLIP/ViT)
                distance=Distance.COSINE  # Лучше для семантического поиска
            ),
        )
        logger.info(f"Created collection: {collection_name}")


# Утилитарные функции для работы с коллекциями
def get_collection_info(client: QdrantClient, collection_name: str):
    """Получить информацию о коллекции"""
    try:
        return client.get_collection(collection_name)
    except Exception as e:
        logger.error(f"Error getting collection {collection_name}: {e}")
        return None

def collection_exists(client: QdrantClient, collection_name: str) -> bool:
    """Проверить существование коллекции"""
    try:
        client.get_collection(collection_name)
        return True
    except Exception:
        return False

migration = QdrantMigrationManager(client)
migration.run_all_migrations()
client.close()