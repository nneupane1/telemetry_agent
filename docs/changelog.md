# Changelog

## [Unreleased]

### Added
- LangGraph workflow layer with deterministic fallback orchestration.
- LangChain prompt-based narrative composer with optional OpenAI runtime.
- Reference dictionary loader and merged signal map support.
- Sample-data execution mode with JSON-backed mart emulation.
- Health endpoint (`/health`) for runtime checks.
- Non-empty deployment artifacts for Compose, Kubernetes, and Terraform bootstrap.
- Fully wired Streamlit operator workflow (evidence, action pack, approval, chat).
- Redesigned React dashboard with API-backed overview/VIN/cohort pages.

### Changed
- Config model now supports `DATA_SOURCE` with `sample` and `databricks` modes.
- VIN interpretation response now includes `evidence_summary`.
- Mart loader now validates VIN/cohort IDs and resolves local sample paths robustly.
- Export route now loads real reference dictionaries for VIN reports.

### Fixed
- Router/service naming drift (`GenAIInterpreter` compatibility alias retained).
- Import-time failures when optional dependencies are absent.
- Placeholder and zero-byte architecture assets replaced with functional scaffolds.

