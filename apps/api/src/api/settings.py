from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="API_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    storage_path: Path = Path("./storage")
    max_upload_bytes: int = 25 * 1024 * 1024


settings = Settings()
