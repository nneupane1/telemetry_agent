import { useRouter } from "next/router"
import { useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"

import ChatbotWidget from "../../components/ChatbotWidget"
import FimPieChart from "../../components/FimPieChart"
import HiGauge from "../../components/HiGauge"
import NeonNavbar from "../../components/NeonNavbar"
import PdfExportPanel from "../../components/PdfExportPanel"
import TrendChart from "../../components/TrendChart"
import {
  CohortInterpretation,
  fetchCohortInterpretation,
} from "../../services/apiClient"

function scoreFromDistribution(distribution?: Record<string, number>) {
  if (!distribution) return 60
  const low = distribution.LOW || 0
  const elevated = distribution.ELEVATED || 0
  const high = distribution.HIGH || 0
  const total = low + elevated + high
  if (total === 0) return 60
  return Math.max(0, Math.min(100, Math.round((low * 100 + elevated * 65 + high * 32) / total)))
}

export default function CohortDetailPage() {
  const router = useRouter()
  const cohort = typeof router.query.cohort === "string" ? router.query.cohort : ""
  const [data, setData] = useState<CohortInterpretation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!cohort) return
    setLoading(true)
    setError(null)
    fetchCohortInterpretation(cohort)
      .then(setData)
      .catch(() => setError("Unable to load cohort interpretation."))
      .finally(() => setLoading(false))
  }, [cohort])

  const trendData = useMemo(() => {
    const base = scoreFromDistribution(data?.risk_distribution)
    return [
      { timestamp: "W-5", value: base + 4 },
      { timestamp: "W-4", value: base + 2 },
      { timestamp: "W-3", value: base, isAnomaly: true },
      { timestamp: "W-2", value: base - 1 },
      { timestamp: "W-1", value: base - 2 },
      { timestamp: "Now", value: base },
    ]
  }, [data?.risk_distribution])

  const distribution = useMemo(
    () =>
      (data?.metrics || []).map((metric) => ({
        name: metric.name,
        value: metric.value,
      })),
    [data?.metrics]
  )

  return (
    <>
      <NeonNavbar />
      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <section className="panel panel-glow p-6">
          <div className="text-kicker">Cohort Intelligence</div>
          <h1 className="text-2xl md:text-3xl">Cohort {cohort || "..."}</h1>
          <p className="text-sm text-text-secondary mt-1">
            Fleet-segment interpretation with anomaly concentration and risk spread.
          </p>
        </section>

        {loading && <div className="panel p-6 text-text-secondary">Loading cohort telemetry...</div>}
        {error && <div className="panel p-6 text-danger">{error}</div>}

        {data && (
          <>
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <HiGauge value={scoreFromDistribution(data.risk_distribution)} />
              <div className="lg:col-span-2">
                <TrendChart title="Cohort Risk Trajectory" data={trendData} />
              </div>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <FimPieChart title="Metric Distribution" data={distribution} />
              <motion.section
                initial={{ opacity: 0, y: 8 }}
                animate={{ opacity: 1, y: 0 }}
                className="panel panel-glow p-6 space-y-4"
              >
                <div className="text-kicker">Narrative Brief</div>
                <h3 className="text-lg">Cohort Summary</h3>
                <p className="text-sm text-text-secondary leading-relaxed">{data.summary}</p>
                <div className="divider" />
                <div className="space-y-2">
                  <div className="text-sm text-text-secondary">Anomalies</div>
                  {data.anomalies.length === 0 ? (
                    <div className="text-sm text-text-muted">No anomalies reported.</div>
                  ) : (
                    data.anomalies.map((anomaly, index) => (
                      <div
                        key={`${anomaly.title}-${index}`}
                        className="rounded-lg border border-neon-orange/30 bg-neon-orange/10 p-3"
                      >
                        <div className="font-display">{anomaly.title}</div>
                        <div className="text-xs text-text-secondary">{anomaly.description}</div>
                      </div>
                    ))
                  )}
                </div>
                <PdfExportPanel subjectType="cohort" subjectId={data.cohort_id} title="Export Cohort Report" />
              </motion.section>
            </section>

            <div className="text-xs text-text-muted">Model version: {data.model_version}</div>
          </>
        )}
      </main>
      {data && <ChatbotWidget context={{ cohort_id: data.cohort_id, risk_distribution: data.risk_distribution }} />}
    </>
  )
}

