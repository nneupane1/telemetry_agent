"""
Reference Data Loader.

Loads semantic reference dictionaries (HI catalog, family maps,
confidence mappings) from YAML / JSON files and persists them
to the configured backend.

Designed to be:
- idempotent
- environment-agnostic
- safe for CI/CD execution
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Dict, Any

import yaml

from app.utils.config import load_config
from app.utils.logger import get_logger

logger = get_logger(__name__)


# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

REFERENCE_DIR = Path("data/reference")

SUPPORTED_EXTENSIONS = {".yaml", ".yml", ".json"}


# ------------------------------------------------------------
# Load helpers
# ------------------------------------------------------------

def _load_file(path: Path) -> Dict[str, Any]:
    """
    Load a single YAML or JSON reference file.
    """
    logger.info("Loading reference file", extra={"path": str(path)})

    if path.suffix in {".yaml", ".yml"}:
        with path.open("r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    if path.suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    raise ValueError(f"Unsupported reference file: {path}")


def _validate_reference(name: str, data: Dict[str, Any]) -> None:
    """
    Minimal structural validation.
    """
    if not isinstance(data, dict):
        raise ValueError(f"Reference '{name}' must be a dictionary")

    if not data:
        raise ValueError(f"Reference '{name}' is empty")

    logger.info(
        "Validated reference",
        extra={"reference": name, "entries": len(data)},
    )


# ------------------------------------------------------------
# Persistence layer (pluggable)
# ------------------------------------------------------------

def _persist_reference(
    *,
    name: str,
    data: Dict[str, Any],
    backend: str,
) -> None:
    """
    Persist reference data to the configured backend.
    """

    # POC default: local JSON snapshot
    if backend == "local":
        out_dir = Path(".reference_cache")
        out_dir.mkdir(exist_ok=True)

        out_path = out_dir / f"{name}.json"
        with out_path.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        logger.info(
            "Reference persisted locally",
            extra={"path": str(out_path)},
        )
        return

    # Future backends (explicit, not magic)
    if backend == "databricks":
        raise NotImplementedError(
            "Databricks reference persistence not yet implemented"
        )

    raise ValueError(f"Unknown reference backend: {backend}")


# ------------------------------------------------------------
# Main execution
# ------------------------------------------------------------

def main() -> None:
    """
    Load and persist all reference files.
    """
    config = load_config()
    backend = config.get("reference_backend", "local")

    if not REFERENCE_DIR.exists():
        logger.error("Reference directory not found")
        sys.exit(1)

    reference_files = [
        p for p in REFERENCE_DIR.iterdir()
        if p.suffix in SUPPORTED_EXTENSIONS
    ]

    if not reference_files:
        logger.error("No reference files found")
        sys.exit(1)

    logger.info(
        "Starting reference data load",
        extra={"file_count": len(reference_files)},
    )

    for path in reference_files:
        name = path.stem
        data = _load_file(path)
        _validate_reference(name, data)
        _persist_reference(
            name=name,
            data=data,
            backend=backend,
        )

    logger.info("Reference data load completed successfully")


if __name__ == "__main__":
    main()
