from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    auth_api_url: str = "http://auth-api:8000"
    redis_url: str = "redis://redis:6379/0"


settings = Settings()
