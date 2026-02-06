"""
Reference dictionary loader.

Loads semantic dictionaries used to translate telemetry signal codes into
human-friendly language. Supports YAML/JSON assets stored in `data/reference`.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional

from app.utils.config import load_config
from app.utils.logger import get_logger, log_event

logger = get_logger(__name__)


class ReferenceLoaderError(RuntimeError):
    pass


class ReferenceLoader:
    def __init__(self, reference_dir: Optional[Path] = None) -> None:
        config = load_config()
        if reference_dir is not None:
            self._reference_dir = reference_dir
        else:
            self._reference_dir = self._resolve_path(config.data.reference_dir)

    @lru_cache(maxsize=1)
    def load_bundle(self) -> Dict[str, Dict[str, Any]]:
        """
        Load all reference dictionaries from disk.
        """
        files = {
            "hi_catalog": "ref_hi_catalog.yaml",
            "hi_family_map": "ref_hi_family_map.yaml",
            "confidence_map": "ref_confidence_map.yaml",
        }

        bundle: Dict[str, Dict[str, Any]] = {}
        for key, filename in files.items():
            path = self._reference_dir / filename
            bundle[key] = self._read_mapping(path)

        log_event(
            logger,
            "Reference dictionaries loaded",
            extra={
                "reference_dir": str(self._reference_dir),
                "catalog_size": len(bundle["hi_catalog"]),
                "family_size": len(bundle["hi_family_map"]),
                "confidence_size": len(bundle["confidence_map"]),
            },
        )

        return bundle

    def load_reference_map(self) -> Dict[str, Dict[str, Any]]:
        """
        Merge catalog and family dictionaries into a code-indexed map.
        """
        bundle = self.load_bundle()
        catalog = bundle.get("hi_catalog", {})
        families = bundle.get("hi_family_map", {})

        merged: Dict[str, Dict[str, Any]] = {}

        for code, raw in catalog.items():
            description = (
                raw.get("description")
                if isinstance(raw, dict)
                else str(raw)
            )
            merged[code] = {
                "description": description or "No description available",
                "family": families.get(code, "UNKNOWN"),
            }

        # Ensure family map-only entries still exist.
        for code, family in families.items():
            if code not in merged:
                merged[code] = {
                    "description": "No description available",
                    "family": family,
                }

        return merged

    def confidence_label(self, score: float) -> str:
        """
        Map confidence scores to human-readable labels.
        """
        confidence_map = self.load_bundle().get("confidence_map", {})
        ranges = confidence_map.get("ranges")
        if not isinstance(ranges, list):
            return "unmapped confidence"

        for bucket in ranges:
            if not isinstance(bucket, dict):
                continue
            minimum = float(bucket.get("min", 0.0))
            maximum = float(bucket.get("max", 1.0))
            if minimum <= score <= maximum:
                return str(bucket.get("label", "unmapped confidence"))

        return "unmapped confidence"

    def _read_mapping(self, path: Path) -> Dict[str, Any]:
        if not path.exists():
            raise ReferenceLoaderError(f"Missing reference file: {path}")

        if path.suffix.lower() == ".json":
            with path.open("r", encoding="utf-8") as handle:
                data = json.load(handle)
        else:
            try:
                import yaml
            except Exception as exc:
                raise ReferenceLoaderError(
                    "PyYAML is required to load YAML reference files."
                ) from exc

            with path.open("r", encoding="utf-8") as handle:
                data = yaml.safe_load(handle)

        if not isinstance(data, dict):
            raise ReferenceLoaderError(
                f"Reference file must contain a mapping object: {path}"
            )

        return data

    @staticmethod
    def _resolve_path(path_value: str) -> Path:
        path = Path(path_value)
        if path.is_absolute() and path.exists():
            return path
        if path.exists():
            return path

        # Package-local fallback for installed distributions.
        package_root = Path(__file__).resolve().parents[1]
        packaged_candidate = package_root / path_value
        if packaged_candidate.exists():
            return packaged_candidate

        repo_root = Path(__file__).resolve().parents[4]
        candidate = repo_root / path_value
        if candidate.exists():
            return candidate

        return path
