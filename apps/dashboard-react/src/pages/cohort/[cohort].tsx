import { useRouter } from "next/router"
import { motion } from "framer-motion"

import NeonNavbar from "../../components/NeonNavbar"
import HiGauge from "../../components/HiGauge"
import TrendChart from "../../components/TrendChart"
import FimPieChart from "../../components/FimPieChart"

import { staggerContainer, staggerItem } from "../../theme/animations"

export default function CohortDetailPage() {
  const router = useRouter()
  const { cohort } = router.query

  // Demo placeholder data (API wiring comes next)
  const cohortHealth = 61

  const trendData = [
    { timestamp: "Week 1", value: 68 },
    { timestamp: "Week 2", value: 66 },
    { timestamp: "Week 3", value: 63, isAnomaly: true },
    { timestamp: "Week 4", value: 61 },
  ]

  const fimData = [
    { name: "Fuel System", value: 42 },
    { name: "Cooling", value: 21 },
    { name: "Electrical", value: 17 },
    { name: "Sensors", value: 12 },
    { name: "Other", value: 8 },
  ]

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
            Cohort Overview
          </h1>
          <p className="text-sm text-text-secondary">
            Fleet segment:{" "}
            <span className="text-neon-purple font-medium">
              {cohort}
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
            <HiGauge value={cohortHealth} />
          </motion.div>

          <motion.div
            variants={staggerItem}
            className="md:col-span-2"
          >
            <TrendChart
              title="Cohort Health Trend"
              data={trendData}
            />
          </motion.div>
        </motion.section>

        {/* Distribution + Narrative */}
        <motion.section
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <motion.div variants={staggerItem}>
            <FimPieChart
              title="Dominant Failure Drivers"
              data={fimData}
            />
          </motion.div>

          <motion.div
            variants={staggerItem}
            className="panel panel-glow p-6 space-y-4"
          >
            <h3 className="text-sm tracking-wide text-text-secondary">
              Cohort Interpretation
            </h3>

            <p className="text-sm leading-relaxed">
              This cohort shows a gradual degradation trend driven
              primarily by fuel system–related signals. While overall
              risk remains elevated rather than critical, the
              concentration of anomalies suggests targeted preventive
              maintenance could significantly reduce downstream impact.
            </p>

            <div className="divider" />

            <p className="text-xs text-text-muted">
              Vehicles affected: 184 · High-risk subset: 27
            </p>
          </motion.div>
        </motion.section>
      </main>
    </>
  )
}
