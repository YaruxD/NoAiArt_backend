from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):


        

    # настройки бд
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    RBC_USER_AUTH_USER: str
    RBC_USER_AUTH_PASSWORD: str
    RBC_USER_AUTH_HOST: str
    RBC_USER_AUTH_PORT: str

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @property
    def RBC_USER_AUTH_URL(self):
        return f"amqp://{self.RBC_USER_AUTH_USER}:{self.RBC_USER_AUTH_PASSWORD}@{self.RBC_USER_AUTH_HOST}:{self.RBC_USER_AUTH_PORT}"
        


    class Config:
        env_file = '.env'

settings = Settings()