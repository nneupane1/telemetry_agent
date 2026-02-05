"""
Configuration Verification Script.

Validates application configuration and environment
before running critical workflows.

Intended to be used in:
- CI pipelines
- pre-deploy hooks
- local sanity checks
"""

from __future__ import annotations

import os
import sys
from typing import Dict, Any

from app.utils.config import load_config
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------
# Required configuration schema
# ------------------------------------------------------------

REQUIRED_KEYS = {
    "api": [
        "host",
        "port",
    ],
    "genai": [
        "provider",
        "model",
    ],
    "reference_backend": [],
}


# ------------------------------------------------------------
# Validators
# ------------------------------------------------------------

def _validate_section(
    section: str,
    config: Dict[str, Any],
) -> None:
    """
    Validate presence of required keys in a section.
    """
    if section not in config:
        raise ValueError(f"Missing config section: '{section}'")

    for key in REQUIRED_KEYS[section]:
        if key not in config[section]:
            raise ValueError(
                f"Missing config key: '{section}.{key}'"
            )


def _validate_env() -> None:
    """
    Validate required environment variables.
    """
    required_env = [
        "API_BASE_URL",
    ]

    missing = [e for e in required_env if not os.getenv(e)]

    if missing:
        raise ValueError(
            f"Missing required environment variables: {missing}"
        )


# ------------------------------------------------------------
# Main execution
# ------------------------------------------------------------

def main() -> None:
    """
    Run configuration verification.
    """
    logger.info("Starting configuration verification")

    config = load_config()

    for section in REQUIRED_KEYS:
        _validate_section(section, config)

    _validate_env()

    logger.info("Configuration verification successful")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error(
            "Configuration verification failed",
            extra={"error": str(exc)},
        )
        sys.exit(1)
