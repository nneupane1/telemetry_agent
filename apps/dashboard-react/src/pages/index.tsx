import { useEffect, useMemo } from "react"
import { motion } from "framer-motion"
import { Building2, Focus, RadioTower, ShieldCheck } from "lucide-react"

import ActionPackViewer from "../components/ActionPackViewer"
import ChatbotWidget from "../components/ChatbotWidget"
import CinematicExecutiveHero from "../components/CinematicExecutiveHero"
import FimPieChart from "../components/FimPieChart"
import HiGauge from "../components/HiGauge"
import NeonNavbar from "../components/NeonNavbar"
import TrendChart from "../components/TrendChart"
import VinExplorer from "../components/VinExplorer"
import {
  defaultVinQueue,
  riskScoreFromLevel,
  useExecutiveDashboardStore,
} from "../store/executiveDashboardStore"

export default function FleetOverviewPage() {
  const vinData = useExecutiveDashboardStore((state) => state.vinData)
  const loading = useExecutiveDashboardStore((state) => state.loading)
  const error = useExecutiveDashboardStore((state) => state.error)
  const cohortSummary = useExecutiveDashboardStore((state) => state.cohortSummary)
  const cinematicMode = useExecutiveDashboardStore((state) => state.cinematicMode)
  const selectedVin = useExecutiveDashboardStore((state) => state.selectedVin)
  const toggleCinematicMode = useExecutiveDashboardStore(
    (state) => state.toggleCinematicMode
  )
  const setSelectedVin = useExecutiveDashboardStore((state) => state.setSelectedVin)
  const loadOverview = useExecutiveDashboardStore((state) => state.loadOverview)

  useEffect(() => {
    void loadOverview(defaultVinQueue)
  }, [loadOverview])

  const averageScore = useMemo(() => {
    if (vinData.length === 0) return 0
    const total = vinData.reduce(
      (acc, vin) => acc + riskScoreFromLevel(vin.risk_level),
      0
    )
    return Math.round(total / vinData.length)
  }, [vinData])

  const spotlightVin =
    vinData.find((vin) => vin.vin === selectedVin) ?? vinData[0] ?? null

  const explorerRows = useMemo(
    () =>
      vinData.map((vin) => ({
        vin: vin.vin,
        risk_level: vin.risk_level,
        hi_score: riskScoreFromLevel(vin.risk_level),
        summary: vin.summary,
      })),
    [vinData]
  )

  const trendData = useMemo(() => {
    const base = spotlightVin
      ? riskScoreFromLevel(spotlightVin.risk_level)
      : averageScore || 56

    return [
      { timestamp: "D-6", value: Math.max(0, base + 7) },
      { timestamp: "D-5", value: Math.max(0, base + 5) },
      { timestamp: "D-4", value: Math.max(0, base + 2), isAnomaly: true },
      { timestamp: "D-3", value: Math.max(0, base + 1) },
      { timestamp: "D-2", value: Math.max(0, base) },
      { timestamp: "D-1", value: Math.max(0, base - 2) },
      { timestamp: "Now", value: Math.max(0, base - 1) },
    ]
  }, [averageScore, spotlightVin])

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

  const spotlightRecommendations = spotlightVin?.recommendations ?? []

  return (
    <>
      <NeonNavbar />

      <main className="max-w-7xl mx-auto px-6 py-10 space-y-8">
        <section className="grid grid-cols-1 xl:grid-cols-[1.45fr_0.55fr] gap-6 items-stretch">
          <CinematicExecutiveHero
            averageScore={averageScore}
            loading={loading}
            error={error}
            cinematicMode={cinematicMode}
            onToggleCinematic={toggleCinematicMode}
          />

          <motion.aside
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            className="panel p-6 space-y-4"
          >
            <div className="text-kicker">Boardroom Feed</div>
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
            {spotlightVin && (
              <div className="rounded-lg border border-neon-cyan/25 bg-neon-cyan/8 p-3">
                <div className="text-xs text-text-muted">Spotlight VIN</div>
                <div className="font-display text-neon-cyan">{spotlightVin.vin}</div>
                <div className="text-xs text-text-secondary mt-1">
                  Risk {spotlightVin.risk_level} | {spotlightRecommendations.length} recommendation(s)
                </div>
              </div>
            )}
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
            title={
              spotlightVin
                ? `Priority Recommendation Snapshot (${spotlightVin.vin})`
                : "Priority Recommendation Snapshot"
            }
            executiveSummary={
              spotlightVin?.summary ||
              "Load VIN telemetry to view generated recommendations."
            }
            recommendations={spotlightRecommendations}
          />
        </section>

        <VinExplorer
          title="High-Value VIN Queue"
          vins={explorerRows}
          selectedVin={selectedVin}
          onSelectVin={setSelectedVin}
        />

        <motion.section
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="panel p-5 flex flex-wrap items-center justify-between gap-3"
        >
          <div className="text-sm text-text-secondary">
            Use this mode in leadership demos to spotlight VINs while keeping operational evidence visible.
          </div>
          <div className="chip-cyan">
            <Focus size={13} className="mr-1.5" />
            Live Spotlight: {selectedVin || "None"}
          </div>
        </motion.section>
      </main>

      <ChatbotWidget />
    </>
  )
}
