from pathlib import Path


def test_backend_health_endpoint_defined():
    main_file = Path("apps/backend-api/app/main.py")
    text = main_file.read_text(encoding="utf-8")
    assert "@app.get(\"/health\"" in text


def test_reference_files_populated():
    required = [
        Path("data/reference/ref_hi_catalog.yaml"),
        Path("data/reference/ref_hi_family_map.yaml"),
        Path("data/reference/ref_confidence_map.yaml"),
    ]
    for path in required:
        assert path.exists()
        assert path.stat().st_size > 0
