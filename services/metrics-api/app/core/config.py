from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://smartsec:smartsec@db:5432/smartsecurity"
    redis_url: str = "redis://redis:6379/0"


settings = Settings()
