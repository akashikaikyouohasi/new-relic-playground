from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_name: str = "new-relic-playground"
    app_version: str = "0.1.0"
    debug: bool = False


settings = Settings()
