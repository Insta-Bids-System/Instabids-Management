import json
from typing import Sequence

from dotenv import load_dotenv
from pydantic import AnyHttpUrl, Field, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    """Application configuration sourced from the environment."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Supabase
    supabase_url: AnyHttpUrl | None = Field(
        default=None, validation_alias="SUPABASE_URL"
    )
    supabase_anon_key: SecretStr | None = Field(
        default=None, validation_alias="SUPABASE_ANON_KEY"
    )
    supabase_service_key: SecretStr | None = Field(
        default=None, validation_alias="SUPABASE_SERVICE_KEY"
    )

    # API
    api_host: str = Field(default="0.0.0.0", validation_alias="API_HOST")
    api_port: int = Field(default=8000, validation_alias="API_PORT")
    api_env: str = Field(default="development", validation_alias="API_ENV")

    # JWT
    jwt_secret_key: SecretStr = Field(
        default=SecretStr("dev-secret-key"), validation_alias="JWT_SECRET_KEY"
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(
        default=60, validation_alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=30, validation_alias="JWT_REFRESH_TOKEN_EXPIRE_DAYS"
    )

    # CORS
    cors_origins: Sequence[str] = Field(
        default=("http://localhost:3000", "http://localhost:3456"), validation_alias="CORS_ORIGINS"
    )

    # Rate Limiting
    rate_limit_requests: int = Field(
        default=100, validation_alias="RATE_LIMIT_REQUESTS"
    )
    rate_limit_period: int = Field(default=3600, validation_alias="RATE_LIMIT_PERIOD")

    # OpenAI / SmartScope
    openai_api_key: SecretStr | None = Field(
        default=None, validation_alias="OPENAI_API_KEY"
    )
    smartscope_model: str = Field(
        default="gpt-4.1-mini", validation_alias="SMARTSCOPE_MODEL"
    )
    smartscope_max_output_tokens: int = Field(
        default=1200, validation_alias="SMARTSCOPE_MAX_OUTPUT_TOKENS"
    )
    smartscope_temperature: float = Field(
        default=0.2, validation_alias="SMARTSCOPE_TEMPERATURE"
    )
    smartscope_confidence_threshold: float = Field(
        default=0.75, validation_alias="SMARTSCOPE_CONFIDENCE_THRESHOLD"
    )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def split_cors_origins(cls, value: object) -> Sequence[str]:
        if isinstance(value, str):
            if value.startswith("["):
                try:
                    parsed = json.loads(value)
                    if isinstance(parsed, list):
                        return tuple(str(origin).strip() for origin in parsed if str(origin).strip())
                except json.JSONDecodeError:
                    pass
            return tuple(origin.strip() for origin in value.split(",") if origin.strip())
        if isinstance(value, (list, tuple)):
            return tuple(value)
        return ("http://localhost:3000",)

    @property
    def supabase_url_value(self) -> str | None:
        return str(self.supabase_url) if self.supabase_url is not None else None

    @property
    def supabase_anon_key_value(self) -> str | None:
        return (
            self.supabase_anon_key.get_secret_value()
            if self.supabase_anon_key is not None
            else None
        )

    @property
    def supabase_service_key_value(self) -> str | None:
        return (
            self.supabase_service_key.get_secret_value()
            if self.supabase_service_key is not None
            else None
        )

    @property
    def jwt_secret_key_value(self) -> str:
        return self.jwt_secret_key.get_secret_value()

    @property
    def openai_api_key_value(self) -> str | None:
        return (
            self.openai_api_key.get_secret_value()
            if self.openai_api_key is not None
            else None
        )


settings = Settings()
