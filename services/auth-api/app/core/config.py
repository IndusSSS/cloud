from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str = "postgresql+asyncpg://smartsec:smartsec@db:5432/smartsecurity"
    secret_key: str = "CHANGE_ME"
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 7


settings = Settings()
