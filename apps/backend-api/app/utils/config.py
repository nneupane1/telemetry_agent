"""
Central configuration management for the GenAI Predictive Interpreter Platform.

Key goals:
- Typed, validated configuration
- Dual data-source support (Databricks Unity Catalog or sample files)
- Optional LLM configuration with OpenAI and OpenAI-compatible providers
"""

from __future__ import annotations

import os
from functools import lru_cache
from typing import Literal, Optional

from pydantic import BaseModel, Field, SecretStr, ValidationError


Environment = Literal["local", "dev", "prod"]
DataSource = Literal["databricks", "sample"]
LLMProvider = Literal["openai", "openai_compatible", "none"]


def _get_env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


class DatabricksConfig(BaseModel):
    host: str = Field(..., description="Databricks workspace URL")
    http_path: str = Field(..., description="SQL Warehouse HTTP path")
    token: SecretStr = Field(..., description="Databricks access token")
    catalog: str = Field(..., description="Unity Catalog catalog name")
    schema_name: str = Field(
        ...,
        alias="schema",
        description="Unity Catalog schema name",
    )

    class Config:
        frozen = True
        allow_population_by_field_name = True


class OpenAIConfig(BaseModel):
    api_key: SecretStr = Field(..., description="OpenAI API key")
    model: str = Field(default="gpt-4.1-mini", description="LLM model")
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    max_tokens: int = Field(default=1024, gt=128)
    base_url: Optional[str] = Field(
        default=None,
        description="Optional OpenAI-compatible API base URL",
    )

    class Config:
        frozen = True


class LLMConfig(BaseModel):
    provider: LLMProvider = Field(default="none")
    openai: Optional[OpenAIConfig] = None

    class Config:
        frozen = True


class DataConfig(BaseModel):
    source: DataSource = Field(
        default="sample",
        description="Primary telemetry source",
    )
    reference_dir: str = Field(default="data/reference")
    sample_file: str = Field(default="data/sample/sample_vin_data.json")

    mart_mh_table: str = Field(default="mart_mh_hi_snapshot_daily")
    mart_mp_table: str = Field(default="mart_mp_triggers_daily")
    mart_fim_table: str = Field(default="mart_fim_rootcause_daily")
    mart_cohort_metrics_table: str = Field(default="mart_cohort_metrics_daily")
    mart_cohort_anomalies_table: str = Field(default="mart_cohort_anomalies_daily")

    class Config:
        frozen = True


class EmailConfig(BaseModel):
    enabled: bool = Field(default=False)
    smtp_host: Optional[str] = None
    smtp_port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[SecretStr] = None
    from_address: Optional[str] = None

    class Config:
        frozen = True


class FeatureFlags(BaseModel):
    enable_genai: bool = True
    enable_langgraph: bool = True
    allow_deterministic_fallback: bool = False
    enable_pdf_export: bool = True
    enable_email_delivery: bool = False
    strict_validation: bool = False

    class Config:
        frozen = True


class AppConfig(BaseModel):
    env: Environment = Field(default="local")
    service_name: str = "genai-predictive-backend"
    log_level: str = Field(default="INFO")

    data: DataConfig
    databricks: Optional[DatabricksConfig] = None
    llm: LLMConfig
    email: EmailConfig
    features: FeatureFlags

    class Config:
        frozen = True


def _load_optional_databricks(source: DataSource) -> Optional[DatabricksConfig]:
    required = [
        "DATABRICKS_HOST",
        "DATABRICKS_HTTP_PATH",
        "DATABRICKS_TOKEN",
        "DATABRICKS_CATALOG",
        "DATABRICKS_SCHEMA",
    ]

    available = [k for k in required if os.getenv(k)]

    if source == "databricks" and len(available) < len(required):
        missing = [k for k in required if not os.getenv(k)]
        raise RuntimeError(
            "DATA_SOURCE=databricks requires Databricks settings: "
            + ", ".join(missing)
        )

    if not available:
        return None

    return DatabricksConfig(
        host=_get_env("DATABRICKS_HOST"),
        http_path=_get_env("DATABRICKS_HTTP_PATH"),
        token=SecretStr(_get_env("DATABRICKS_TOKEN")),
        catalog=_get_env("DATABRICKS_CATALOG"),
        schema_name=_get_env("DATABRICKS_SCHEMA"),
    )


def _load_llm() -> LLMConfig:
    provider_raw = (os.getenv("LLM_PROVIDER") or "").strip().lower()
    llm_api_key = os.getenv("LLM_API_KEY")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    api_key = llm_api_key or openai_api_key
    base_url = os.getenv("LLM_BASE_URL")

    if provider_raw and provider_raw not in {"openai", "openai_compatible", "none"}:
        raise RuntimeError(
            "LLM_PROVIDER must be one of: openai, openai_compatible, none"
        )

    if not api_key:
        return LLMConfig(provider="none", openai=None)

    provider: LLMProvider
    if provider_raw:
        provider = provider_raw  # type: ignore[assignment]
    else:
        provider = "openai_compatible" if base_url else "openai"

    if provider == "none":
        return LLMConfig(provider="none", openai=None)

    if provider == "openai_compatible" and not base_url:
        raise RuntimeError(
            "LLM_PROVIDER=openai_compatible requires LLM_BASE_URL"
        )

    openai_cfg = OpenAIConfig(
        api_key=SecretStr(api_key),
        model=os.getenv("LLM_MODEL", os.getenv("OPENAI_MODEL", "gpt-4.1-mini")),
        temperature=float(
            os.getenv("LLM_TEMPERATURE", os.getenv("OPENAI_TEMPERATURE", "0.2"))
        ),
        max_tokens=int(
            os.getenv("LLM_MAX_TOKENS", os.getenv("OPENAI_MAX_TOKENS", "1024"))
        ),
        base_url=base_url,
    )
    return LLMConfig(provider=provider, openai=openai_cfg)


@lru_cache(maxsize=1)
def load_config() -> AppConfig:
    """
    Load and validate runtime configuration.
    """

    try:
        env: Environment = _get_env("APP_ENV", "local")  # type: ignore
        data_source: DataSource = _get_env("DATA_SOURCE", "sample")  # type: ignore

        data = DataConfig(
            source=data_source,
            reference_dir=os.getenv("REFERENCE_DIR", "data/reference"),
            sample_file=os.getenv("SAMPLE_DATA_FILE", "data/sample/sample_vin_data.json"),
            mart_mh_table=os.getenv("MART_MH_TABLE", "mart_mh_hi_snapshot_daily"),
            mart_mp_table=os.getenv("MART_MP_TABLE", "mart_mp_triggers_daily"),
            mart_fim_table=os.getenv("MART_FIM_TABLE", "mart_fim_rootcause_daily"),
            mart_cohort_metrics_table=os.getenv(
                "MART_COHORT_METRICS_TABLE",
                "mart_cohort_metrics_daily",
            ),
            mart_cohort_anomalies_table=os.getenv(
                "MART_COHORT_ANOMALIES_TABLE",
                "mart_cohort_anomalies_daily",
            ),
        )

        databricks = _load_optional_databricks(data_source)
        llm = _load_llm()

        email = EmailConfig(
            enabled=_env_bool("EMAIL_ENABLED", False),
            smtp_host=os.getenv("SMTP_HOST"),
            smtp_port=int(os.getenv("SMTP_PORT", "0")) or None,
            username=os.getenv("SMTP_USERNAME"),
            password=SecretStr(os.getenv("SMTP_PASSWORD"))
            if os.getenv("SMTP_PASSWORD")
            else None,
            from_address=os.getenv("EMAIL_FROM"),
        )

        features = FeatureFlags(
            enable_genai=_env_bool("FEATURE_GENAI", True),
            enable_langgraph=_env_bool("FEATURE_LANGGRAPH", True),
            allow_deterministic_fallback=_env_bool(
                "FEATURE_ALLOW_DETERMINISTIC_FALLBACK",
                False,
            ),
            enable_pdf_export=_env_bool("FEATURE_PDF", True),
            enable_email_delivery=_env_bool("FEATURE_EMAIL", False),
            strict_validation=env == "prod",
        )

        # In production, block sample mode by default.
        if env == "prod" and data_source != "databricks":
            raise RuntimeError(
                "APP_ENV=prod requires DATA_SOURCE=databricks."
            )

        return AppConfig(
            env=env,
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            data=data,
            databricks=databricks,
            llm=llm,
            email=email,
            features=features,
        )

    except ValidationError as exc:
        raise RuntimeError(f"Invalid configuration: {exc}") from exc
