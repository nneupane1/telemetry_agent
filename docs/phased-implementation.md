# Phased Implementation Plan

## Goal
Move from demo-safe behavior to production-grade, real-data behavior without a big-bang rewrite.

## Phase 1: Transport and Runtime Hardening (Now)
- Keep REST as primary transport.
- Enable WebSocket fallback for chat when REST latency breaches tolerance repeatedly.
- Keep LangGraph-first orchestration enabled.
- Keep deterministic fallback only as controlled resilience.

## Phase 2: Real Data Onboarding
- Ingest real MH / MP / FIM schemas and sample slices.
- Validate VIN/cohort keys, event timestamps, and type consistency.
- Map raw fields into canonical marts:
  - `mart_mh_hi_snapshot_daily`
  - `mart_mp_triggers_daily`
  - `mart_fim_rootcause_daily`
  - `mart_cohort_metrics_daily`
  - `mart_cohort_anomalies_daily`
- Expand reference YAML mappings and schema validation checks.

## Phase 3: Interpretation Quality Upgrade
- Replace deterministic-heavy agent internals with stronger model-backed logic where data quality permits.
- Keep bounded prompts and grounding constraints.
- Add regression tests against approved telemetry scenarios and expected narratives.

## Phase 4: Dashboard Contract Completion
- Replace hardcoded cohort/VIN assumptions with backend-driven endpoints.
- Add cohort list/filters/search APIs.
- Align chart data to backend time-series contracts rather than local synthetic traces.

## Phase 5: Production Controls
- Add authN/authZ for all write and sensitive read paths.
- Add request limits, audit depth, and SLO alerting.
- Add rollout guardrails (canary/feature flags) for model and prompt updates.

## Execution Rule
Only promote to the next phase after:
- Schema contract tests pass.
- API compatibility tests pass.
- Dashboard end-to-end validation passes.
