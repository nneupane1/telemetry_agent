import axios, { AxiosInstance } from "axios"

// ------------------------------------------------------------
// Configuration
// ------------------------------------------------------------

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

// ------------------------------------------------------------
// Axios instance
// ------------------------------------------------------------

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
})

// ------------------------------------------------------------
// Domain types (aligned with backend models)
// ------------------------------------------------------------

export interface EvidenceItem {
  source_model: string
  signal_code: string
  signal_description: string
  confidence: number
  observed_at?: string
}

export interface Recommendation {
  title: string
  rationale: string
  urgency: "LOW" | "MEDIUM" | "HIGH"
  suggested_action?: string
  evidence: EvidenceItem[]
}

export interface VinInterpretation {
  vin: string
  summary: string
  risk_level: "LOW" | "ELEVATED" | "HIGH" | "CRITICAL"
  recommendations: Recommendation[]
  model_version: string
}

export interface CohortMetric {
  name: string
  value: number
  unit?: string
  description?: string
}

export interface CohortAnomaly {
  title: string
  description: string
  affected_vin_count: number
  severity: string
  related_signals?: string[]
}

export interface CohortInterpretation {
  cohort_id: string
  summary: string
  metrics: CohortMetric[]
  anomalies: CohortAnomaly[]
  risk_distribution?: Record<string, number>
  model_version: string
}

// ------------------------------------------------------------
// API functions
// ------------------------------------------------------------

export async function fetchVinInterpretation(
  vin: string
): Promise<VinInterpretation> {
  const { data } = await api.get<VinInterpretation>(`/vin/${vin}`)
  return data
}

export async function fetchCohortInterpretation(
  cohortId: string
): Promise<CohortInterpretation> {
  const { data } = await api.get<CohortInterpretation>(
    `/cohort/${cohortId}`
  )
  return data
}

export async function createActionPack(payload: {
  subject_type: string
  subject_id: string
  title: string
  executive_summary: string
  recommendations: Recommendation[]
}) {
  const { data } = await api.post("/action-pack", payload)
  return data
}
