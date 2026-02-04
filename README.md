





genai-predictive-platform/
│
├── apps/
│   ├── backend-api/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── routers/
│   │   │   │   ├── vin.py
│   │   │   │   ├── action_pack.py
│   │   │   │   └── cohort.py
│   │   │   ├── services/
│   │   │   │   ├── genai_interpreter.py
│   │   │   │   ├── pdf_exporter.py
│   │   │   │   ├── email_sender.py
│   │   │   │   └── mart_loader.py
│   │   │   ├── agents/
│   │   │   │   ├── vin_explainer_agent.py
│   │   │   │   ├── cohort_brief_agent.py
│   │   │   │   └── evidence_agent.py
│   │   │   ├── models/
│   │   │   │   ├── vin.py
│   │   │   │   ├── cohort.py
│   │   │   │   └── action_pack.py
│   │   │   ├── utils/
│   │   │   │   ├── logger.py
│   │   │   │   ├── config.py
│   │   │   │   └── databricks_conn.py
│   │   │   ├── tests/
│   │   │   │   ├── test_vin.py
│   │   │   │   └── test_genai_interpreter.py
│   │   │   └── __init__.py
│   │   ├── Dockerfile
│   │   └── requirements.txt
│   ├── dashboard-react/
│   │   ├── public/
│   │   │   ├── logo.svg
│   │   │   └── neon-bg.jpg
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── VinExplorer.tsx
│   │   │   │   ├── TrendChart.tsx
│   │   │   │   ├── HiGauge.tsx
│   │   │   │   ├── FimPieChart.tsx
│   │   │   │   ├── ActionPackViewer.tsx
│   │   │   │   ├── ChatbotWidget.tsx
│   │   │   │   └── NeonNavbar.tsx
│   │   │   ├── pages/
│   │   │   │   ├── index.tsx
│   │   │   │   ├── vin/[vin].tsx
│   │   │   │   └── cohort/[cohort].tsx
│   │   │   ├── theme/
│   │   │   │   ├── neonTheme.ts
│   │   │   │   └── animations.ts
│   │   │   ├── services/
│   │   │   │   └── apiClient.ts
│   │   │   ├── styles/
│   │   │   │   └── globals.css
│   │   │   └── utils/
│   │   │       └── formatters.ts
│   │   ├── tests/
│   │   │   ├── VinExplorer.test.tsx
│   │   │   └── ChatbotWidget.test.tsx
│   │   ├── Dockerfile
│   │   └── package.json
│   ├── dashboard-streamlit/
│   │   ├── app/
│   │   │   ├── main.py
│   │   │   ├── pages/
│   │   │   │   ├── dashboard.py
│   │   │   │   ├── evidence.py
│   │   │   │   └── approval.py
│   │   │   ├── components/
│   │   │   │   ├── VinLookup.py
│   │   │   │   ├── CohortExplorer.py
│   │   │   │   └── EvidenceViewer.py
│   │   │   └── theme/
│   │   │       └── streamlit_neon_theme.css
│   │   ├── requirements.txt
│   │   └── Dockerfile
│
├── data/
│   ├── reference/
│   │   ├── ref_hi_catalog.yaml
│   │   ├── ref_hi_family_map.yaml
│   │   └── ref_confidence_map.yaml
│   ├── marts/
│   │   ├── mart_mh_hi_snapshot_daily.sql
│   │   ├── mart_mp_triggers_daily.sql
│   │   └── mart_fim_rootcause_daily.sql
│   └── sample/
│       ├── sample_vin_data.json
│       └── sample_action_pack.json
│
├── deployments/
│   ├── k8s/
│   │   └── api-deployment.yaml
│   ├── docker-compose.yaml
│   └── terraform/
│       └── main.tf
│
├── docs/
│   ├── architecture.md
│   ├── api-spec.yaml
│   ├── onboarding.md
│   ├── ui-styleguide.md
│   └── changelog.md
│
├── scripts/
│   ├── data_ingest/
│   │   └── load_reference_data.py
│   ├── db_migration/
│   │   └── upgrade_schema.py
│   └── utils/
│       └── verify_config.py
│
├── tests/
│   ├── integration/
│   │   └── test_api_integration.py
│   ├── e2e/
│   │   └── test_dashboard_e2e.py
│   └── load/
│       └── test_loadgen.py
│
├── .env.example
├── .gitignore
├── README.md
└── LICENSE
