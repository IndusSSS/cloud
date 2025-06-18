from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    stripe_secret: str = ""
    razorpay_secret: str = ""


settings = Settings()
