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

    # trip app settings
    MAX_PARTICIPANTS: int = 10

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def db_url(self):
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


def get_settings():
    return Settings()
