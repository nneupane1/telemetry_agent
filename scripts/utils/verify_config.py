"""
Configuration verification script.
"""

from __future__ import annotations

from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "apps" / "backend-api"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.utils.config import load_config
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


def main() -> None:
    config = load_config()

    if config.data.source == "databricks" and config.databricks is None:
        raise RuntimeError(
            "DATA_SOURCE=databricks requires Databricks credentials"
        )

    reference_dir = Path(config.data.reference_dir)
    if not reference_dir.exists():
        raise RuntimeError(
            f"Reference directory missing: {reference_dir}"
        )

    sample_file = Path(config.data.sample_file)
    if config.data.source == "sample" and not sample_file.exists():
        raise RuntimeError(
            f"Sample data file missing: {sample_file}"
        )

    if (
        not config.features.enable_langgraph
        and not config.features.allow_deterministic_fallback
    ):
        raise RuntimeError(
            "FEATURE_LANGGRAPH=false requires FEATURE_ALLOW_DETERMINISTIC_FALLBACK=true"
        )

    log_event(
        logger,
        "Configuration verification successful",
        extra={
            "env": config.env,
            "data_source": config.data.source,
            "reference_dir": str(reference_dir),
            "sample_file": str(sample_file),
            "langgraph_enabled": config.features.enable_langgraph,
            "allow_deterministic_fallback": config.features.allow_deterministic_fallback,
        },
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        logger.error(str(exc))
        sys.exit(1)
