from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_name: str = "MySpot"
    environment: str = "local"
    secret_key: str = "change-me-in-production"
    debug: bool = True

    database_url: str = "sqlite:///./myspot.db"
    redis_url: str = "redis://localhost:6379/0"


settings = Settings()
