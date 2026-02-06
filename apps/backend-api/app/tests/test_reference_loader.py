from pathlib import Path

from app.services.reference_loader import ReferenceLoader


def test_reference_loader_merges_catalog_and_family(tmp_path: Path):
    (tmp_path / "ref_hi_catalog.yaml").write_text(
        "HI-1001:\n  description: Turbo variance\n",
        encoding="utf-8",
    )
    (tmp_path / "ref_hi_family_map.yaml").write_text(
        "HI-1001: AIR_MANAGEMENT\n",
        encoding="utf-8",
    )
    (tmp_path / "ref_confidence_map.yaml").write_text(
        "ranges:\n  - min: 0.70\n    max: 1.00\n    label: high confidence\n",
        encoding="utf-8",
    )

    loader = ReferenceLoader(reference_dir=tmp_path)
    merged = loader.load_reference_map()

    assert "HI-1001" in merged
    assert merged["HI-1001"]["description"] == "Turbo variance"
    assert merged["HI-1001"]["family"] == "AIR_MANAGEMENT"
    assert loader.confidence_label(0.8) == "high confidence"

