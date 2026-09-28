from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    environment: str = "development"
    database_url: str = f"sqlite:///{BASE_DIR / 'fitbuddy.db'}"
    gemini_api_key: str = Field("", validation_alias="GEMINI_API_KEY")
    gemini_workout_model: str = Field("gemini-2.5-pro", validation_alias="GEMINI_WORKOUT_MODEL")
    gemini_tip_model: str = Field("gemini-3.8-flash", validation_alias="GEMINI_TIP_MODEL")
    admin_token: str = Field("change-me", validation_alias="ADMIN_TOKEN")
    admin_session_secret: str = Field("change-this-session-secret", validation_alias="ADMIN_SESSION_SECRET")
    model_timeout_seconds: int = 60
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

@lru_cache
def get_settings(): return Settings()
settings=get_settings()
