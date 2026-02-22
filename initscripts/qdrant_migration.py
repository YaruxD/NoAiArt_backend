import os
import logging
import sys
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
from settings import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class QdrantMigrationManager:
    def __init__(self, client: QdrantClient):
        self.client = client
    
    def run_all_migrations(self):
        """Запуск всех миграций"""
        logger.info(f"Starting migrations for Qdrant at {settings.QDRANT_URL}")
        self._create_image_collection()
    
    def _create_image_collection(self):
        """Основная коллекция для изображений/пинов"""
        collection_name = settings.COLLECTION_NAME
        
        try:
            # Проверяем существование коллекции
            self.client.get_collection(collection_name)
            logger.info(f"✅ Collection '{collection_name}' already exists")
            return
        except Exception as e:
            logger.info(f"Collection '{collection_name}' not found, creating...")
        
        # Создаем коллекцию
        self.client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=settings.VECTOR_SIZE,
                distance=Distance.COSINE
            ),
        )
        logger.info(f"✅ Created collection: {collection_name} with size={settings.VECTOR_SIZE}")

def collection_exists(client: QdrantClient, collection_name: str) -> bool:
    """Проверить существование коллекции"""
    try:
        client.get_collection(collection_name)
        return True
    except Exception:
        return False

def main():
    logger.info(f"Connecting to Qdrant at {settings.QDRANT_URL}")
    client = QdrantClient(settings.QDRANT_URL)
    
    try:
        # Проверяем доступность Qdrant
        client.get_collections()
        logger.info("✅ Connected to Qdrant successfully")
        
        # Запускаем миграции
        migration = QdrantMigrationManager(client)
        migration.run_all_migrations()
        
        # Проверяем результат
        if collection_exists(client, settings.COLLECTION_NAME):
            logger.info(f"✅ Migration completed successfully - collection '{settings.COLLECTION_NAME}' is ready")
        else:
            logger.error(f"❌ Migration failed - collection '{settings.COLLECTION_NAME}' not found after creation")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        sys.exit(1)
    finally:
        client.close()

if __name__ == "__main__":
    main()