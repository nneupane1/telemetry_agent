"""
Configuration loading tests.
"""

from __future__ import annotations

import pytest

from app.utils.config import load_config


@pytest.fixture(autouse=True)
def _reset_config_cache():
    load_config.cache_clear()
    yield
    load_config.cache_clear()


def test_load_openai_compatible_llm(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("DATA_SOURCE", "sample")
    monkeypatch.setenv("LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.setenv("LLM_BASE_URL", "https://llm.example.com/v1")
    monkeypatch.setenv("LLM_MODEL", "qwen-3-235b")
    monkeypatch.setenv("LLM_TEMPERATURE", "0.1")
    monkeypatch.setenv("LLM_MAX_TOKENS", "900")

    cfg = load_config()

    assert cfg.llm.provider == "openai_compatible"
    assert cfg.llm.openai is not None
    assert cfg.llm.openai.model == "qwen-3-235b"
    assert cfg.llm.openai.base_url == "https://llm.example.com/v1"
    assert cfg.llm.openai.temperature == 0.1
    assert cfg.llm.openai.max_tokens == 900


def test_openai_compatible_requires_base_url(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("DATA_SOURCE", "sample")
    monkeypatch.setenv("LLM_PROVIDER", "openai_compatible")
    monkeypatch.setenv("LLM_API_KEY", "test-key")
    monkeypatch.delenv("LLM_BASE_URL", raising=False)

    with pytest.raises(RuntimeError, match="LLM_PROVIDER=openai_compatible requires LLM_BASE_URL"):
        load_config()


def test_emergency_fallback_flag(monkeypatch):
    monkeypatch.setenv("APP_ENV", "local")
    monkeypatch.setenv("DATA_SOURCE", "sample")
    monkeypatch.setenv("FEATURE_ALLOW_DETERMINISTIC_FALLBACK", "true")

    cfg = load_config()

    assert cfg.features.allow_deterministic_fallback is True
