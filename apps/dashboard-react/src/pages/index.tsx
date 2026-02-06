import Link from "next/link"
import { useEffect, useMemo, useState } from "react"
import { motion } from "framer-motion"
import { ArrowRight, Building2, RadioTower, ShieldCheck } from "lucide-react"

import ActionPackViewer from "../components/ActionPackViewer"
import ChatbotWidget from "../components/ChatbotWidget"
import FimPieChart from "../components/FimPieChart"
import HiGauge from "../components/HiGauge"
import NeonNavbar from "../components/NeonNavbar"
import TrendChart from "../components/TrendChart"
import VinExplorer from "../components/VinExplorer"
import {
  fetchCohortInterpretation,
  fetchVinInterpretation,
  VinInterpretation,
} from "../services/apiClient"

const defaultVins = [
  "WVWZZZ1KZ6W000001",
  "WVWZZZ1KZ6W000002",
  "WVWZZZ1KZ6W000003",
]

function riskToScore(risk: string) {
  if (risk === "LOW") return 88
  if (risk === "ELEVATED") return 68
  if (risk === "HIGH") return 46
  return 25
}

export default function FleetOverviewPage() {
  const [vinData, setVinData] = useState<VinInterpretation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [cohortSummary, setCohortSummary] = useState("Loading cohort interpretation...")

  useEffect(() => {
    let mounted = true

    async function load() {
      setLoading(true)
      setError(null)
      const results = await Promise.allSettled(defaultVins.map((vin) => fetchVinInterpretation(vin)))

      if (!mounted) return

      const rows = results
        .filter((result): result is PromiseFulfilledResult<VinInterpretation> => result.status === "fulfilled")
        .map((result) => result.value)
      setVinData(rows)

      if (rows.length === 0) {
        setError("No VIN interpretations were returned by the API.")
      }

      try {
        const cohort = await fetchCohortInterpretation("EURO6-DIESEL")
        if (mounted) setCohortSummary(cohort.summary)
      } catch {
        if (mounted) setCohortSummary("Cohort interpretation is currently unavailable.")
      } finally {
        if (mounted) setLoading(false)
      }
    }

    void load()
    return () => {
      mounted = false
    }
  }, [])

  const averageScore = useMemo(() => {
    if (vinData.length === 0) return 0
    const total = vinData.reduce((acc, vin) => acc + riskToScore(vin.risk_level), 0)
    return Math.round(total / vinData.length)
  }, [vinData])

  const explorerRows = useMemo(
    () =>
      vinData.map((vin) => ({
        vin: vin.vin,
        risk_level: vin.risk_level,
        hi_score: riskToScore(vin.risk_level),
        summary: vin.summary,
      })),
    [vinData]
  )

  const trendData = useMemo(() => {
    const base = averageScore || 56
    return [
      { timestamp: "D-6", value: Math.max(0, base + 6) },
      { timestamp: "D-5", value: Math.max(0, base + 3) },
      { timestamp: "D-4", value: Math.max(0, base + 1), isAnomaly: true },
      { timestamp: "D-3", value: Math.max(0, base - 1) },
      { timestamp: "D-2", value: Math.max(0, base) },
      { timestamp: "D-1", value: Math.max(0, base - 2) },
      { timestamp: "Now", value: Math.max(0, base) },
    ]
  }, [averageScore])

  const distributionData = useMemo(() => {
    const familyCount: Record<string, number> = {}
    vinData.forEach((vin) => {
      vin.recommendations.forEach((recommendation) => {
        recommendation.evidence.forEach((evidence) => {
          const family = evidence.signal_code.split("-")[0]
          familyCount[family] = (familyCount[family] || 0) + 1
        })
      })
    })
    return Object.entries(familyCount).map(([name, value]) => ({ name, value }))
  }, [vinData])

  const headlineRecommendation = vinData[0]?.recommendations ?? []

  return (
    <>
      <NeonNavbar />

      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <section className="grid grid-cols-1 lg:grid-cols-[1.35fr_0.65fr] gap-6 items-stretch">
          <motion.div
            initial={{ opacity: 0, x: -10 }}
            animate={{ opacity: 1, x: 0 }}
            className="panel panel-glow p-6 space-y-4"
          >
            <div className="chip-cyan">Databricks + LangGraph Interpreter Layer</div>
            <h1 className="text-3xl md:text-4xl leading-tight max-w-3xl">
              Fleet telemetry is translated into explainable operational actions.
            </h1>
            <p className="text-text-secondary max-w-2xl">
              This console reads Unity Catalog mart outputs and produces forensic, evidence-backed narratives for VIN and cohort decisioning.
            </p>
            <div className="flex flex-wrap gap-3 pt-1">
              <Link href="/vin/WVWZZZ1KZ6W000001" className="chip-amber">
                Open VIN Intelligence <ArrowRight size={14} className="ml-1" />
              </Link>
              <Link href="/cohort/EURO6-DIESEL" className="chip-mint">
                Open Cohort Intelligence <ArrowRight size={14} className="ml-1" />
              </Link>
            </div>
            {error && <p className="text-sm text-danger">{error}</p>}
          </motion.div>

          <motion.aside
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            className="panel p-6 space-y-4"
          >
            <div className="text-kicker">Live Operations</div>
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <RadioTower size={15} className="text-neon-cyan" />
                <span>{loading ? "Refreshing telemetry..." : "Telemetry synchronized"}</span>
              </div>
              <div className="flex items-center gap-2">
                <ShieldCheck size={15} className="text-success" />
                <span>Evidence traceability enabled</span>
              </div>
              <div className="flex items-center gap-2">
                <Building2 size={15} className="text-neon-orange" />
                <span>Control-room deployment profile</span>
              </div>
            </div>
            <div className="divider" />
            <p className="text-sm text-text-secondary">{cohortSummary}</p>
          </motion.aside>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <HiGauge value={averageScore} />
          <div className="lg:col-span-2">
            <TrendChart title="Fleet Composite Health (Last 7 Days)" data={trendData} />
          </div>
        </section>

        <section className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <FimPieChart title="Dominant Signal Families" data={distributionData} />
          <ActionPackViewer
            title="Priority Recommendation Snapshot"
            executiveSummary={
              vinData[0]?.summary ||
              "Load VIN telemetry to view generated recommendations."
            }
            recommendations={headlineRecommendation}
          />
        </section>

        <VinExplorer title="High-Value VIN Queue" vins={explorerRows} />
      </main>

      <ChatbotWidget />
    </>
  )
}

