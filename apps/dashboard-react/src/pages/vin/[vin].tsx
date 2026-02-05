import { useRouter } from "next/router"
import { motion } from "framer-motion"

import NeonNavbar from "../../components/NeonNavbar"
import HiGauge from "../../components/HiGauge"
import TrendChart from "../../components/TrendChart"
import ActionPackViewer from "../../components/ActionPackViewer"

import { staggerContainer, staggerItem } from "../../theme/animations"

export default function VinDetailPage() {
  const router = useRouter()
  const { vin } = router.query

  // Demo placeholder data (API wiring comes next)
  const hiScore = 42

  const trendData = [
    { timestamp: "Mon", value: 58 },
    { timestamp: "Tue", value: 54 },
    { timestamp: "Wed", value: 49, isAnomaly: true },
    { timestamp: "Thu", value: 46 },
    { timestamp: "Fri", value: 42 },
  ]

  const actionPack = {
    title: "VIN Action Pack",
    executiveSummary:
      "Predictive signals indicate a high likelihood of fuel system degradation. Immediate inspection is recommended to avoid service disruption.",
    recommendations: [
      {
        title: "Inspect Fuel Pressure System",
        rationale:
          "Fuel pressure instability detected with high confidence across recent telemetry windows.",
        urgency: "HIGH" as const,
        evidence: [
          {
            signal_code: "HI-4302",
            signal_description: "Fuel pressure instability detected",
            confidence: 0.91,
          },
        ],
      },
      {
        title: "Monitor Sensor Drift",
        rationale:
          "Secondary sensor drift patterns observed but not yet critical.",
        urgency: "MEDIUM" as const,
        evidence: [
          {
            signal_code: "HI-2210",
            signal_description: "Sensor signal drift detected",
            confidence: 0.72,
          },
        ],
      },
    ],
  }

  return (
    <>
      <NeonNavbar />

      <main className="max-w-7xl mx-auto px-6 py-10 space-y-10">
        {/* Header */}
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.35 }}
          className="space-y-2"
        >
          <h1 className="text-2xl font-semibold tracking-wide">
            VIN Overview
          </h1>
          <p className="text-sm text-text-secondary">
            Vehicle Identification Number:{" "}
            <span className="text-neon-cyan font-medium">
              {vin}
            </span>
          </p>
        </motion.section>

        {/* KPIs */}
        <motion.section
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <motion.div variants={staggerItem}>
            <HiGauge value={hiScore} />
          </motion.div>

          <motion.div
            variants={staggerItem}
            className="md:col-span-2"
          >
            <TrendChart
              title="VIN Health Trend"
              data={trendData}
              color="#FF4FD8"
            />
          </motion.div>
        </motion.section>

        {/* Action Pack */}
        <motion.section
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
        >
          <motion.div variants={staggerItem}>
            <ActionPackViewer
              title={actionPack.title}
              executiveSummary={actionPack.executiveSummary}
              recommendations={actionPack.recommendations}
            />
          </motion.div>
        </motion.section>
      </main>
    </>
  )
}
