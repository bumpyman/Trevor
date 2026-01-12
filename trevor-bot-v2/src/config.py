"""Configuration management for Trevor Bot."""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Bot Tokens
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    whatsapp_account_sid: Optional[str] = Field(None, env="WHATSAPP_ACCOUNT_SID")
    whatsapp_auth_token: Optional[str] = Field(None, env="WHATSAPP_AUTH_TOKEN")
    whatsapp_number: Optional[str] = Field(None, env="WHATSAPP_NUMBER")
    messenger_page_token: Optional[str] = Field(None, env="MESSENGER_PAGE_TOKEN")
    messenger_verify_token: Optional[str] = Field(None, env="MESSENGER_VERIFY_TOKEN")

    # LLM Configuration
    anthropic_api_key: str = Field(..., env="ANTHROPIC_API_KEY")
    openai_api_key: Optional[str] = Field(None, env="OPENAI_API_KEY")
    use_local_llm: bool = Field(False, env="USE_LOCAL_LLM")
    ollama_base_url: str = Field("http://localhost:11434", env="OLLAMA_BASE_URL")

    # Database
    database_url: str = Field(..., env="DATABASE_URL")

    # FHIR
    fhir_base_url: str = Field("http://localhost:8080/fhir", env="FHIR_BASE_URL")

    # Email
    sendgrid_api_key: str = Field(..., env="SENDGRID_API_KEY")
    hug_hematology_email: str = Field("hematology@hug.ch", env="HUG_HEMATOLOGY_EMAIL")
    from_email: str = Field(..., env="FROM_EMAIL")

    # Application
    environment: str = Field("development", env="ENVIRONMENT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    secret_key: str = Field(..., env="SECRET_KEY")

    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
