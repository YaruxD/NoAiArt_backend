from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.JWT_PRIVATE_KEY = self._load_key(self.JWT_PRIVATE_KEY_PATH)
        self.JWT_PUBLIC_KEY = self._load_key(self.JWT_PUBLIC_KEY_PATH)

    # настройки бд
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str


    # настройки producer_user_auth
    RBP_USER_AUTH_USER: str
    RBP_USER_AUTH_PASSWORD: str
    RBP_USER_AUTH_HOST: str
    RBP_USER_AUTH_PORT: str
    

    # jwt
    JWT_PRIVATE_KEY_PATH: str 
    JWT_PUBLIC_KEY_PATH: str 
    JWT_ALGORITHM: str

    JWT_PRIVATE_KEY: str = ""
    JWT_PUBLIC_KEY: str = ""


    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def RBP_USER_AUTH_URL(self):
        return f"amqp://{self.RBP_USER_AUTH_USER}:{self.RBP_USER_AUTH_PASSWORD}@{self.RBP_USER_AUTH_HOST}:{self.RBP_USER_AUTH_PORT}"
    
    def _load_key(self, key_path: str) -> str:
        path = Path(key_path)
        if not path.exists():
            raise FileNotFoundError(f"Key file not found: {path}")
        return path.read_text()

    class Config:
        env_file = '.env'

settings = Settings()


