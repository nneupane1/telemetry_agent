# Changelog

All notable changes to the GenAI Predictive Interpreter Platform
are documented in this file.

This project follows a pragmatic, human-readable change log
focused on architectural and functional evolution.

---

## [Unreleased]

### Planned
- LangGraph graph definitions formalized as first-class artifacts
- Persistent approval storage (Delta / PostgreSQL)
- Authentication and role-based access control
- Email delivery integration for PDF reports

---

## [1.0.0] – Initial End-to-End POC

### Added
- GenAI interpretation layer on top of existing MH / MP / FIM predictive models
- Agent-based explanation workflows for VIN-level and cohort-level insights
- Reference layer for semantic mapping of health indices and confidence levels
- FastAPI backend exposing interpretation, chat, export, and approval endpoints
- React + Next.js business dashboard with cinematic, animated UX
- Streamlit operator dashboard with evidence review and approval workflows
- Deterministic PDF export for VIN and cohort reports
- Human-in-the-loop approval system with audit trail
- CI-safe scripts for reference loading, schema migration, and config verification
- OpenAPI specification documenting all backend endpoints

### Architectural Decisions
- GenAI is strictly limited to interpretation; predictive models remain unchanged
- All GenAI orchestration is centralized in a single service layer
- No GenAI logic is embedded in frontend components
- Evidence transparency and operator approval are mandatory before action

### Notes
- This release is intended as a production-credible proof of concept
- Interfaces and services are designed for extension without breaking changes

---

## [0.1.0] – Internal Prototype

### Added
- Initial project structure
- Placeholder dashboards and mock data flows
- Early agent and mart design experiments
