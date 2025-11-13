from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.JWT_PUBLIC_KEY = self._load_key(self.JWT_PUBLIC_KEY_PATH)

    #jwt для декодирования токенов (RSA256)
    JWT_PUBLIC_KEY_PATH: str 
    JWT_ALGORITHM: str
    JWT_PUBLIC_KEY: str = ""

    #настройка микросервисов (gateway)

    #AuthService
    AUTH_SERVICE_HOST: str
    AUTH_SERVICE_PORT: str
    
    @property
    def AUTH_SERVICE_URL(self):
        return f"http://{self.AUTH_SERVICE_HOST}:{self.AUTH_SERVICE_PORT}"

    def _load_key(self, key_path: str) -> str:
        path = Path(key_path)
        if not path.exists():
            raise FileNotFoundError(f"Key file not found: {path}")
        return path.read_text()
    
    #UserService
    USER_SERVICE_HOST: str
    USER_SERVICE_PORT: str
    
    @property
    def USER_SERVICE_URL(self):
        return f"http://{self.USER_SERVICE_HOST}:{self.USER_SERVICE_PORT}"


    

    class Config:
        env_file = '.env'

settings = Settings()