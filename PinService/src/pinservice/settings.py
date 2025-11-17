from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    # s3
    S3_ACCESS_KEY: str
    S3_SECRET_KEY: str
    S3_PICTURE_BUCKET_NAME: str
    S3_URL: str

    @property
    def DATABASE_URL_asyncpg(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"


settings = Settings()
