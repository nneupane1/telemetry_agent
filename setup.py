from __future__ import annotations

from pathlib import Path
from typing import List

from setuptools import find_packages, setup


ROOT = Path(__file__).resolve().parent


def _read_text(path: Path) -> str:
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def _read_requirements(path: Path) -> List[str]:
    if not path.exists():
        return []

    requirements: List[str] = []
    for raw_line in path.read_text(encoding="utf-8-sig").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        requirements.append(line)
    return requirements


backend_reqs = _read_requirements(ROOT / "apps" / "backend-api" / "requirements.txt")
runtime_reqs = [req for req in backend_reqs if not req.lower().startswith("pytest")]
test_reqs = [req for req in backend_reqs if req.lower().startswith("pytest")]
streamlit_reqs = _read_requirements(
    ROOT / "apps" / "dashboard-streamlit" / "requirements.txt"
)

extras = {
    "test": test_reqs,
    "streamlit": streamlit_reqs,
}
extras["dev"] = sorted(set(test_reqs + streamlit_reqs))


setup(
    name="telemetry-agent-backend",
    version="1.1.0",
    description="GenAI telemetry interpretation backend with LangGraph orchestration.",
    long_description=_read_text(ROOT / "README.md"),
    long_description_content_type="text/markdown",
    author="Telemetry Agent Team",
    url="https://github.com/nneupane1/telemetry_agent",
    python_requires=">=3.10",
    package_dir={"": "apps/backend-api"},
    packages=find_packages(where="apps/backend-api", include=["app", "app.*"]),
    include_package_data=True,
    package_data={
        "app": [
            "data/reference/*.yaml",
            "data/sample/*.json",
        ]
    },
    install_requires=runtime_reqs,
    extras_require=extras,
    entry_points={
        "console_scripts": [
            "telemetry-backend=app.cli:main",
            "telemetry-backend-dev=app.cli:dev_main",
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: FastAPI",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    keywords=[
        "telemetry",
        "langgraph",
        "fastapi",
        "predictive-maintenance",
    ],
    project_urls={
        "Documentation": "https://github.com/nneupane1/telemetry_agent#readme",
        "Source": "https://github.com/nneupane1/telemetry_agent",
    },
)
