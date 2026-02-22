from pydantic_settings import BaseSettings
from pydantic import ConfigDict

class Settings(BaseSettings):
    QDRANT_URL: str = "http://qdrant:6333"
    COLLECTION_NAME: str = "images"
    VECTOR_SIZE: int = 512
    DISTANCE: str = "Cosine"
    
    model_config = ConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()