import { useRouter } from "next/router"
import { useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"

import ActionPackViewer from "../../components/ActionPackViewer"
import ChatbotWidget from "../../components/ChatbotWidget"
import HiGauge from "../../components/HiGauge"
import NeonNavbar from "../../components/NeonNavbar"
import PdfExportPanel from "../../components/PdfExportPanel"
import TrendChart from "../../components/TrendChart"
import {
  fetchVinInterpretation,
  recordApproval,
  VinInterpretation,
} from "../../services/apiClient"

function scoreFromRisk(risk: string) {
  if (risk === "LOW") return 90
  if (risk === "ELEVATED") return 66
  if (risk === "HIGH") return 44
  return 24
}

export default function VinDetailPage() {
  const router = useRouter()
  const vin = typeof router.query.vin === "string" ? router.query.vin.toUpperCase() : ""

  const [data, setData] = useState<VinInterpretation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [approvalNote, setApprovalNote] = useState("")
  const [approvalStatus, setApprovalStatus] = useState<string | null>(null)

  useEffect(() => {
    if (!vin) return
    setLoading(true)
    setError(null)
    fetchVinInterpretation(vin)
      .then(setData)
      .catch(() => setError("Unable to load VIN interpretation."))
      .finally(() => setLoading(false))
  }, [vin])

  const trendData = useMemo(() => {
    const base = scoreFromRisk(data?.risk_level ?? "ELEVATED")
    return [
      { timestamp: "D-6", value: base + 8 },
      { timestamp: "D-5", value: base + 5 },
      { timestamp: "D-4", value: base + 1 },
      { timestamp: "D-3", value: base, isAnomaly: true },
      { timestamp: "D-2", value: base - 2 },
      { timestamp: "D-1", value: base - 1 },
      { timestamp: "Now", value: base },
    ]
  }, [data?.risk_level])

  async function submitApproval(decision: "approve" | "reject" | "escalate") {
    if (!data) return
    try {
      await recordApproval({
        subject_type: "vin",
        subject_id: data.vin,
        decision,
        comment: approvalNote || `Decision ${decision} submitted from VIN page.`,
        decided_by: "dashboard-user",
      })
      setApprovalStatus(`Decision '${decision}' recorded.`)
    } catch {
      setApprovalStatus("Approval API call failed.")
    }
  }

  return (
    <>
      <NeonNavbar />
      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <section className="panel panel-glow p-6">
          <div className="text-kicker">VIN Intelligence</div>
          <h1 className="text-2xl md:text-3xl">VIN {vin || "..."}</h1>
          <p className="text-sm text-text-secondary mt-1">
            Deep-dive interpretation generated from MH/MP/FIM telemetry marts.
          </p>
        </section>

        {loading && <div className="panel p-6 text-text-secondary">Loading VIN telemetry...</div>}
        {error && <div className="panel p-6 text-danger">{error}</div>}

        {data && (
          <>
            <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <HiGauge value={scoreFromRisk(data.risk_level)} />
              <div className="lg:col-span-2">
                <TrendChart title="VIN Stability Trace" data={trendData} />
              </div>
            </section>

            <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <ActionPackViewer
                title="Generated Recommendations"
                executiveSummary={data.summary}
                recommendations={data.recommendations}
              />
              <div className="space-y-6">
                <PdfExportPanel subjectType="vin" subjectId={data.vin} title="Export VIN Report" />

                <motion.section
                  initial={{ opacity: 0, y: 8 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="panel p-5 space-y-4"
                >
                  <div className="text-kicker">Approval Workflow</div>
                  <h3 className="text-base">Record control-room decision</h3>
                  <textarea
                    value={approvalNote}
                    onChange={(event) => setApprovalNote(event.target.value)}
                    placeholder="Provide decision rationale..."
                    className="w-full min-h-[110px] rounded-lg bg-bg-secondary border border-neon-cyan/25 px-3 py-2 text-sm outline-none focus:border-neon-cyan/55"
                  />
                  <div className="flex flex-wrap gap-2">
                    <button className="chip-cyan" onClick={() => void submitApproval("approve")}>
                      Approve
                    </button>
                    <button className="chip-amber" onClick={() => void submitApproval("escalate")}>
                      Escalate
                    </button>
                    <button className="chip border-danger/45 bg-danger/12 text-danger" onClick={() => void submitApproval("reject")}>
                      Reject
                    </button>
                  </div>
                  {approvalStatus && <p className="text-sm text-text-secondary">{approvalStatus}</p>}
                </motion.section>
              </div>
            </section>

            <div className="text-xs text-text-muted">Model version: {data.model_version}</div>
          </>
        )}
      </main>

      {data && <ChatbotWidget context={{ vin: data.vin, risk_level: data.risk_level, evidence_summary: data.evidence_summary }} />}
    </>
  )
}

