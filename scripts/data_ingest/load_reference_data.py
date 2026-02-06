"""
Reference Data Validation and Cache Builder.

Validates semantic dictionaries and writes normalized cache artifacts used by
the backend runtime.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
BACKEND_ROOT = REPO_ROOT / "apps" / "backend-api"
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.services.reference_loader import ReferenceLoader
from app.utils.config import load_config
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output-dir",
        default=".reference_cache",
        help="Directory where normalized reference JSON files are written",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = load_config()
    loader = ReferenceLoader()

    bundle = loader.load_bundle()
    merged = loader.load_reference_map()

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for name, payload in bundle.items():
        out_path = out_dir / f"{name}.json"
        out_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    merged_path = out_dir / "reference_map.json"
    merged_path.write_text(json.dumps(merged, indent=2), encoding="utf-8")

    log_event(
        logger,
        "Reference cache generation complete",
        extra={
            "source_dir": config.data.reference_dir,
            "output_dir": str(out_dir),
            "signals": len(merged),
        },
    )


if __name__ == "__main__":
    main()
