import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # DB settings
    POSTGRES_PASSWORD: str
    DB_DRIVER: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    # JWT settings
    JWT_SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    # redis cache settings
    CACHE_HOST: str
    CACHE_PORT: int
    CACHE_DB: int
    REDIS_URL: str

    # trip app settings
    MAX_PARTICIPANTS: int = 10

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MEDIA_ROOT: str = os.path.join(BASE_DIR, "media")
    PDF_DIR: str = os.path.join(MEDIA_ROOT, "pdfs")

    # rabbitmq settings
    RABBITMQ_URL: str
    RABBIT_PORT: int
    RABBIT_CONTROL_PANEL_PORT: int

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def db_url(self):
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


def get_settings():
    return Settings()
