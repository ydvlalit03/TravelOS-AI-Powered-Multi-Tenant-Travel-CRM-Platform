"""Application configuration loaded from environment / .env."""
from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # --- Core ---
    environment: Literal["development", "staging", "production"] = "development"
    secret_key: str = "change-me"
    credentials_encryption_key: str = ""  # Fernet key for per-tenant secrets

    # --- Database ---
    database_url: str = (
        "postgresql+asyncpg://travelos:travelos@localhost:5432/travelos"
    )

    # --- Redis ---
    redis_url: str = "redis://localhost:6379/0"

    # --- Auth ---
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 14
    jwt_algorithm: str = "HS256"

    # --- LLM providers ---
    gemini_api_key: str = ""
    gemini_text_model: str = "gemini-2.5-flash"
    gemini_image_model: str = "gemini-2.5-flash-image"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    llm_text_provider: Literal["gemini", "groq", "mock"] = "gemini"
    # Default to keyless mock posters; set to "gemini" (needs GEMINI_API_KEY) for
    # real images. Pollinations' free tier now often returns 402.
    llm_image_provider: Literal["gemini", "pollinations", "mock"] = "mock"

    # --- Email / SMS (Phase 2) ---
    email_provider: Literal["console", "resend", "brevo"] = "console"
    resend_api_key: str = ""
    brevo_api_key: str = ""
    email_from: str = "hello@travelos.local"
    sms_provider: Literal["console", "msg91", "fast2sms"] = "console"
    msg91_api_key: str = ""
    fast2sms_api_key: str = ""

    # --- WhatsApp Cloud API (Phase 4) ---
    whatsapp_provider: Literal["console", "cloud"] = "console"
    whatsapp_phone_number_id: str = ""
    whatsapp_token: str = ""
    whatsapp_verify_token: str = "travelos-wa-verify"

    # --- CRM / followups ---
    followup_delay_minutes: int = 1440  # gap between sequence steps (default 1 day)
    followup_max_steps: int = 2  # reminders after the first touch
    scheduler_interval_seconds: int = 60  # how often the worker scans due followups

    # --- Meta (Phase 2/3) ---
    meta_app_id: str = ""
    meta_app_secret: str = ""
    meta_webhook_verify_token: str = "travelos-verify"

    # --- Storage ---
    storage_backend: Literal["local", "s3"] = "local"
    s3_bucket: str = ""
    aws_region: str = "ap-south-1"

    # --- CORS ---
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
        ]
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
