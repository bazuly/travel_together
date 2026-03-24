from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_DRIVER: str
    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)

    @property
    def db_url(self):
        return f"{self.DB_DRIVER}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


def get_settings():
    return Settings()  # type: ignore
