from __future__ import annotations
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Global application settings (similar to C# AppSettings/Options)."""

    app_name: str = Field(default="Movie Analytics Platform")
    environment: str = Field(default="dev")
    data_folder: str = Field(default="data")
    reports_folder: str = Field(default="reports")

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_prefix="MOVIE_APP_",
        env_file=".env",
    )


settings = Settings()
