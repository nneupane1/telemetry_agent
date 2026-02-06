import json
from pathlib import Path

import pytest

from app.services.mart_loader import MartLoader, MartLoaderError
from app.utils.config import load_config


def test_mart_loader_reads_sample_mode(tmp_path: Path, monkeypatch):
    sample_path = tmp_path / "sample_vin_data.json"
    sample_path.write_text(
        json.dumps(
            {
                "vins": [
                    {
                        "vin": "WVWZZZ1KZ6W000001",
                        "mh": [{"hi_code": "HI-4302", "confidence": 0.9, "observed_at": "2026-02-01T00:00:00Z"}],
                        "mp": [{"signal_code": "MP-110", "confidence": 0.8, "trigger_time": "2026-02-01T01:00:00Z"}],
                        "fim": [{"signal_code": "FIM-22", "confidence": 0.85, "observed_at": "2026-02-01T02:00:00Z"}],
                    }
                ],
                "cohorts": [
                    {
                        "cohort_id": "EURO6-DIESEL",
                        "metrics": [{"metric_name": "risk_high", "metric_value": 3}],
                        "anomalies": [{"title": "Fuel cluster", "description": "Spike", "affected_vin_count": 2, "severity": "HIGH"}],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("DATA_SOURCE", "sample")
    monkeypatch.setenv("SAMPLE_DATA_FILE", str(sample_path))
    load_config.cache_clear()

    loader = MartLoader()
    assert len(loader.load_mh_snapshot("WVWZZZ1KZ6W000001")) == 1
    assert len(loader.load_mp_triggers("WVWZZZ1KZ6W000001")) == 1
    assert len(loader.load_fim_root_causes("WVWZZZ1KZ6W000001")) == 1
    assert len(loader.load_cohort_metrics("EURO6-DIESEL")) == 1
    assert len(loader.load_cohort_anomalies("EURO6-DIESEL")) == 1
    cohorts = loader.list_cohorts()
    assert cohorts == [
        {
            "cohort_id": "EURO6-DIESEL",
            "cohort_description": None,
        }
    ]
    load_config.cache_clear()


def test_mart_loader_drops_invalid_rows_when_not_strict(
    tmp_path: Path,
    monkeypatch,
):
    sample_path = tmp_path / "sample_vin_data.json"
    sample_path.write_text(
        json.dumps(
            {
                "vins": [
                    {
                        "vin": "WVWZZZ1KZ6W000001",
                        "mh": [
                            {
                                "hi_code": "HI-4302",
                                "confidence": 0.9,
                                "observed_at": "2026-02-01T00:00:00Z",
                            },
                            {
                                "confidence": 0.7,
                                "observed_at": "2026-02-01T00:10:00Z",
                            },
                        ],
                        "mp": [],
                        "fim": [],
                    }
                ],
                "cohorts": [],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("DATA_SOURCE", "sample")
    monkeypatch.setenv("SAMPLE_DATA_FILE", str(sample_path))
    monkeypatch.setenv("APP_ENV", "local")
    load_config.cache_clear()

    loader = MartLoader()
    rows = loader.load_mh_snapshot("WVWZZZ1KZ6W000001")

    assert len(rows) == 1
    assert rows[0]["hi_code"] == "HI-4302"
    load_config.cache_clear()


def test_mart_loader_raises_on_invalid_row_in_strict_mode(
    tmp_path: Path,
    monkeypatch,
):
    sample_path = tmp_path / "sample_vin_data.json"
    sample_path.write_text(
        json.dumps(
            {
                "vins": [
                    {
                        "vin": "WVWZZZ1KZ6W000001",
                        "mh": [
                            {
                                "confidence": 0.7,
                                "observed_at": "2026-02-01T00:10:00Z",
                            }
                        ],
                        "mp": [],
                        "fim": [],
                    }
                ],
                "cohorts": [],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("DATA_SOURCE", "sample")
    monkeypatch.setenv("SAMPLE_DATA_FILE", str(sample_path))
    monkeypatch.setenv("APP_ENV", "local")
    load_config.cache_clear()

    loader = MartLoader()
    loader._config = loader._config.copy(
        update={
            "features": loader._config.features.copy(
                update={"strict_validation": True}
            )
        }
    )

    with pytest.raises(MartLoaderError):
        loader.load_mh_snapshot("WVWZZZ1KZ6W000001")

    load_config.cache_clear()


def test_mart_loader_rejects_invalid_sample_schema(
    tmp_path: Path,
    monkeypatch,
):
    sample_path = tmp_path / "sample_vin_data.json"
    sample_path.write_text(
        json.dumps(
            {
                "vins": [
                    {
                        "vin": "WVWZZZ1KZ6W000001",
                        "mh": [],
                        "mp": [],
                        "fim": [],
                    }
                ],
                "cohorts": [
                    {
                        "metrics": [],
                        "anomalies": [],
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.setenv("DATA_SOURCE", "sample")
    monkeypatch.setenv("SAMPLE_DATA_FILE", str(sample_path))
    load_config.cache_clear()

    loader = MartLoader()
    with pytest.raises(MartLoaderError):
        loader.load_cohort_metrics("EURO6-DIESEL")

    load_config.cache_clear()
