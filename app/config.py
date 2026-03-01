from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # デフォルトで未定義のフィールドを禁止しているので、extra="ignore"で許可
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "new-relic-playground"
    app_version: str = "0.1.0"
    debug: bool = False


settings = Settings()
