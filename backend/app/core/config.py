"""Application configuration loaded from environment / .env."""
from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
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

    # --- Background scheduler ---
    # Run in-process (single-process dev). In multi-worker prod, set false on the
    # web service and run the dedicated worker (python -m app.workers.run) instead,
    # so the scheduler isn't duplicated across web workers.
    run_scheduler: bool = True

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
    # Public base URL for stored assets (e.g. a CloudFront domain). Falls back to
    # the S3 virtual-hosted URL. Required for real IG publishing (Graph API fetches
    # the image by public URL).
    asset_public_base_url: str = ""

    # --- CORS ---
    # Accepts a JSON list or a comma-separated string in CORS_ORIGINS.
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://localhost:3000",
        ]
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_csv(cls, v: object) -> object:
        if isinstance(v, str) and not v.strip().startswith("["):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    def require_production_secrets(self) -> None:
        """Fail fast if production is misconfigured."""
        if self.environment != "production":
            return
        problems = []
        if self.secret_key in ("", "change-me"):
            problems.append("SECRET_KEY must be set")
        if not self.credentials_encryption_key:
            problems.append("CREDENTIALS_ENCRYPTION_KEY must be set")
        if self.storage_backend == "s3" and not self.s3_bucket:
            problems.append("S3_BUCKET required when STORAGE_BACKEND=s3")
        if problems:
            raise RuntimeError("Invalid production config: " + "; ".join(problems))


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
