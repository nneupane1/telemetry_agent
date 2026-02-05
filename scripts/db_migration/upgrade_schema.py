"""
Schema Upgrade Script.

Applies forward-only schema migrations in a controlled,
idempotent, and auditable manner.

Designed for:
- local POC
- CI pipelines
- production migrations (with backend swap)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Callable, Dict

from app.utils.config import load_config
from app.utils.logger import get_logger

logger = get_logger(__name__)

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

SCHEMA_STATE_FILE = Path(".schema_version.json")

MigrationFn = Callable[[], None]


# ------------------------------------------------------------
# Migration registry
# ------------------------------------------------------------

def migration_001_initial() -> None:
    """
    Initial schema bootstrap.

    Creates baseline structures required by the platform.
    """
    logger.info("Applying migration 001: initial schema")

    # POC placeholder:
    # - create tables
    # - initialize Delta schemas
    # - prepare approval logs table

    # Intentionally explicit; no side effects hidden
    logger.info("Initial schema created")


def migration_002_add_approval_store() -> None:
    """
    Add approval decision persistence schema.
    """
    logger.info("Applying migration 002: approval store")

    # Example:
    # CREATE TABLE approval_decisions (...)
    logger.info("Approval store schema added")


# Ordered, forward-only migrations
MIGRATIONS: Dict[int, MigrationFn] = {
    1: migration_001_initial,
    2: migration_002_add_approval_store,
}


# ------------------------------------------------------------
# State helpers
# ------------------------------------------------------------

def _load_current_version() -> int:
    if not SCHEMA_STATE_FILE.exists():
        return 0

    with SCHEMA_STATE_FILE.open("r", encoding="utf-8") as f:
        state = json.load(f)
        return int(state.get("version", 0))


def _persist_version(version: int) -> None:
    with SCHEMA_STATE_FILE.open("w", encoding="utf-8") as f:
        json.dump({"version": version}, f, indent=2)


# ------------------------------------------------------------
# Main execution
# ------------------------------------------------------------

def main(dry_run: bool = False) -> None:
    """
    Apply pending schema migrations.
    """
    _ = load_config()  # future backend selection hook

    current_version = _load_current_version()
    latest_version = max(MIGRATIONS.keys())

    logger.info(
        "Schema migration check",
        extra={
            "current_version": current_version,
            "latest_version": latest_version,
            "dry_run": dry_run,
        },
    )

    if current_version >= latest_version:
        logger.info("Schema is already up to date")
        return

    for version in range(current_version + 1, latest_version + 1):
        migration = MIGRATIONS.get(version)
        if not migration:
            raise RuntimeError(f"Missing migration for version {version}")

        logger.info(f"Preparing migration {version}")

        if dry_run:
            logger.info(f"[DRY RUN] Would apply migration {version}")
            continue

        migration()
        _persist_version(version)

        logger.info(f"Migration {version} applied successfully")

    logger.info("All migrations completed")


if __name__ == "__main__":
    dry = "--dry-run" in sys.argv
    main(dry_run=dry)
