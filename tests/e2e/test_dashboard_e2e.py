from pathlib import Path


def test_react_pages_are_not_placeholder():
    home = Path("apps/dashboard-react/src/pages/index.tsx").read_text(encoding="utf-8")
    approval = Path("apps/dashboard-streamlit/app/main.py").read_text(encoding="utf-8")

    assert "Placeholder demo data" not in home
    assert "will be loaded here" not in approval
