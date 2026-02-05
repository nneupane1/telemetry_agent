# GenAI Interpretation Layer Architecture Summary

## Overview

The GenAI interpretation layer serves as a **non‑intrusive interface** above the existing predictive models used for heavy‑duty vehicle maintenance. These models are **unchanged** and include:

- **Machine Health (MH):** hundreds of engineered health indices (HIs), reliability metrics and modelled symptoms.
- **Maintenance Prediction (MP):** trigger probabilities indicating when attention is needed.
- **Failure Impact Model (FIM):** probabilities for different root causes.

These predictive outputs reside in Delta tables within the Unity Catalog. The GenAI layer interprets these outputs into clear, human‑readable explanations **without changing the underlying predictive logic**.

## Data Layer (Existing Models)

- **Stored Data:** MH, MP and FIM predictions are stored as Delta tables. These tables encode all troubleshooting logic.  
- **Assumptions:** No repair manuals, OEM procedures or retrievable diagnostic steps are needed; everything is already encoded in the data.

## Mart Layer

To make the raw Delta tables usable by agents, small **mart tables** (views) are created. Key characteristics:

- **Simplified Views:** Marts like `mart_mh_hi_snapshot_daily`, `mart_mp_triggers_daily`, `mart_fim_rootcause_daily` and `mart_hi_cohorts_daily` flatten and filter the original tables, making them smaller and more predictable.  
- **Agent‑Friendly:** The marts reduce the number of columns to manageable levels, since agents cannot consume 200+ columns directly.

## Reference Layer

The reference layer provides **tiny semantic dictionaries** that map machine codes to human‑readable terms. It includes:

| Reference Table         | Purpose                                                  | Example Mapping                                          |
|-------------------------|-----------------------------------------------------------|----------------------------------------------------------|
| **ref_hi_catalog**       | Map health‑index codes to descriptive labels             | `EGR_HI` → “EGR system performance”; `SCRUFR_HI` → “SCR efficiency” |
| **ref_hi_family_map**    | Group HIs into families                                  | `SCRUFR_HI` → “SCR family”; `EGR_HI` → “EGR family”       |
| **ref_confidence_map**   | Translate probabilities into confidence descriptors       | ≥0.7 → “high confidence”; 0.4–0.7 → “moderate confidence” |

These tables are **not diagnostic procedures**; they simply standardize terminology and confidence phrases.

## Agentic Interpretation Layer

LangGraph multi‑agents perform the interpretation. The pipeline consists of several specialized agents:

1. **Cohort Detective** – identifies high‑risk VINs, rising clusters and emerging patterns using MH/MP/FIM metrics.
2. **RCA Interpreter** – reads the predictive data for a single VIN and converts HIs, trigger probabilities and root‑cause probabilities into human‑readable sentences using the reference layer for terminology.
3. **Context Builder** – adds time‑based context (e.g., last 7 days trends) and reliability patterns to the narrative.
4. **Action Pack Composer** – assembles the predictive summary at the VIN level. It describes anomalies, indicates the likely family of failure, states the model confidence and recommends when to schedule inspection (but **does not provide repair instructions**).
5. **QA Agent** – performs quality‑assurance checks, ensuring no missing values and consistent language throughout the output.

The result is a **VIN‑level written explanation** of what the predictive model sees, with structured evidence.

## Backend – FastAPI Server

A FastAPI server exposes endpoints to access the data and generated explanations:

- `/vin/{vin}` – returns all MH/MP/FIM values and the corresponding GenAI summary.  
- `/vin/{vin}/pack` – provides the full predictive action pack.  
- `/vin/{vin}/pdf` – exports the report as a PDF using tools like WeasyPrint or ReportLab.  
- `/vin/{vin}/email` – emails the PDF to a technician.

The backend connects to Databricks to fetch mart tables, runs the LangGraph agents, and returns JSON for the UI while handling PDF generation and email delivery.

## Frontends (Two UIs)

Both UIs communicate with the same FastAPI backend:

1. **React + Next.js Dashboard (Primary UI)** – a full‑featured dashboard showing:  
   - VIN explorer with trend charts, health‑index gauges, root‑cause pie charts and trigger probability bars.  
   - A predictive action pack viewer with options to download the PDF or send it via email.

2. **Streamlit Dashboard (Internal Operator UI)** – a simplified internal tool providing VIN lookup, explanation viewing, cohort exploration, and an approval system with evidence viewing.

## Outputs Generated

The GenAI system produces several outputs:

- **Predictive Action Pack:** summarises the likely failure family, model interpretation of HIs and root‑cause probabilities, trigger detection, trends, confidence and recommended operational timing (e.g., “schedule within 48 h”).
- **Engineer Cohort Brief:** provides a fleet‑level summary of predictive anomalies, helping engineers prioritise vehicles or groups.
- **Evidence Summary:** lists the MH/MP/FIM fields used to generate the explanation.
- **PDF Export:** a formatted report ready for download or email.

## Benefits of the New Architecture

This architecture solves current issues where a control room team manually interprets raw predictive outputs. Benefits include:

- **Automated Interpretation:** agents produce consistent, clear explanations rapidly, reducing interpretation time from hours to seconds.
- **Standardized Language:** the reference layer ensures uniform terminology and confidence descriptions.
- **Scalability:** the system can generate VIN‑level reports across thousands of vehicles without manual intervention.
- **Structured Evidence and Approval:** the evidence summary and approval workflows add transparency and auditability.
- **Seamless Integration:** React/Next.js and Streamlit UIs integrate with the FastAPI backend, enabling PDF and email workflows without changing the underlying predictive models.

## Final Summary

The new architecture introduces a **GenAI interpretation layer** that sits atop the existing MH, MP and FIM predictive models stored in Delta tables. Small marts simplify these tables for agent consumption, and human‑readable reference dictionaries translate machine codes to consistent terminology. LangGraph multi‑agents then convert the predictive outputs into coherent VIN‑level narratives, cohort briefs and recommended operational actions. A FastAPI backend exposes these interpretations to a React/Next.js dashboard and an internal Streamlit UI, also offering PDF export and email capabilities. The control room continues to monitor and decide on maintenance, while the GenAI layer automates the repetitive task of explaining what the predictive models see, thus scaling standardized reporting across large fleets.
