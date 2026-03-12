from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):


    NEO4J_URI: str
    NEO4J_USER: str
    NEO4J_PASSWORD: str

    RBC_FOLLOW_AUTH_USER: str
    RBC_FOLLOW_AUTH_PASSWORD: str
    RBC_FOLLOW_AUTH_HOST: str
    RBC_FOLLOW_AUTH_PORT: str


    @property
    def RBC_FOLLOW_AUTH_URL(self):
        return f"amqp://{self.RBC_FOLLOW_AUTH_USER}:{self.RBC_FOLLOW_AUTH_PASSWORD}@{self.RBC_FOLLOW_AUTH_HOST}:{self.RBC_FOLLOW_AUTH_PORT}"
        


    class Config:
        env_file = '.env'

settings = Settings()