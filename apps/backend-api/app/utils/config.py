"""
Central configuration management for the GenAI Predictive Interpreter Platform.

Design principles:
- Strong typing & validation (Pydantic)
- Environment-aware (local / dev / prod)
- No hardcoded secrets
- LLM-provider agnostic
- Safe defaults for POC, strict for prod
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal, Optional

from pydantic import BaseModel, Field, SecretStr, ValidationError


# ---------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------

Environment = Literal["local", "dev", "prod"]


def _get_env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


# ---------------------------------------------------------------------
# Databricks Configuration
# ---------------------------------------------------------------------

class DatabricksConfig(BaseModel):
    """
    Databricks / Unity Catalog configuration.
    """

    host: str = Field(..., description="Databricks workspace URL")
    http_path: str = Field(..., description="SQL Warehouse HTTP path")
    token: SecretStr = Field(..., description="Databricks access token")
    catalog: str = Field(..., description="Unity Catalog name")
    schema: str = Field(..., description="Default schema")

    class Config:
        frozen = True


# ---------------------------------------------------------------------
# LLM Configuration
# ---------------------------------------------------------------------

class OpenAIConfig(BaseModel):
    """
    OpenAI configuration (primary for POC).
    """

    api_key: SecretStr = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4.1-mini", description="LLM model name")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, gt=128)

    class Config:
        frozen = True


class LLMConfig(BaseModel):
    """
    Abstract LLM configuration.
    Extend this to support OSS models (LLaMA, Mistral, etc.).
    """

    provider: Literal["openai"] = Field(default="openai")
    openai: Optional[OpenAIConfig] = None

    class Config:
        frozen = True


# ---------------------------------------------------------------------
# Email / Reporting Configuration
# ---------------------------------------------------------------------

class EmailConfig(BaseModel):
    """
    SMTP email configuration for report delivery.
    """

    enabled: bool = Field(default=False)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    from_address: Optional[str] = None

    class Config:
        frozen = True


# ---------------------------------------------------------------------
# Feature Flags
# ---------------------------------------------------------------------

class FeatureFlags(BaseModel):
    """
    Feature flags for controlling behavior across environments.
    """

    enable_genai: bool = True
    enable_pdf_export: bool = True
    enable_email_delivery: bool = False
    strict_validation: bool = False

    class Config:
        frozen = True


# ---------------------------------------------------------------------
# Application Configuration
# ---------------------------------------------------------------------

class AppConfig(BaseModel):
    """
    Root application configuration object.
    """

    env: Environment
    service_name: str = "genai-predictive-backend"
    log_level: str = Field(default="INFO")

    databricks: DatabricksConfig
    llm: LLMConfig
    email: EmailConfig
    features: FeatureFlags

    class Config:
        frozen = True


# ---------------------------------------------------------------------
# Config Loader
# ---------------------------------------------------------------------

@lru_cache(maxsize=1)
def load_config() -> AppConfig:
    """
    Load and validate application configuration.
    Cached to ensure singleton behavior.
    """

    try:
        env: Environment = _get_env("APP_ENV", "local")  # type: ignore

        databricks = DatabricksConfig(
            host=_get_env("DATABRICKS_HOST"),
            http_path=_get_env("DATABRICKS_HTTP_PATH"),
            token=SecretStr(_get_env("DATABRICKS_TOKEN")),
            catalog=_get_env("DATABRICKS_CATALOG"),
            schema=_get_env("DATABRICKS_SCHEMA"),
        )

        openai_cfg = OpenAIConfig(
            api_key=SecretStr(_get_env("OPENAI_API_KEY")),
            model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
            temperature=float(os.getenv("OPENAI_TEMPERATURE", "0.2")),
            max_tokens=int(os.getenv("OPENAI_MAX_TOKENS", "1024")),
        )

        llm = LLMConfig(
            provider="openai",
            openai=openai_cfg,
        )

        email = EmailConfig(
            enabled=os.getenv("EMAIL_ENABLED", "false").lower() == "true",
            smtp_host=os.getenv("SMTP_HOST"),
            smtp_port=int(os.getenv("SMTP_PORT", "0")) or None,
            username=os.getenv("SMTP_USERNAME"),
            password=SecretStr(os.getenv("SMTP_PASSWORD")) if os.getenv("SMTP_PASSWORD") else None,
            from_address=os.getenv("EMAIL_FROM"),
        )

        features = FeatureFlags(
            enable_genai=os.getenv("FEATURE_GENAI", "true").lower() == "true",
            enable_pdf_export=os.getenv("FEATURE_PDF", "true").lower() == "true",
            enable_email_delivery=os.getenv("FEATURE_EMAIL", "false").lower() == "true",
            strict_validation=env == "prod",
        )

        return AppConfig(
            env=env,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            databricks=databricks,
            llm=llm,
            email=email,
            features=features,
        )

    except ValidationError as e:
        raise RuntimeError(f"Invalid configuration: {e}") from e
