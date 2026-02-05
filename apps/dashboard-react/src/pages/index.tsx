import { motion } from "framer-motion"

import NeonNavbar from "../components/NeonNavbar"
import HiGauge from "../components/HiGauge"
import TrendChart from "../components/TrendChart"
import FimPieChart from "../components/FimPieChart"

import { staggerContainer, staggerItem } from "../theme/animations"

export default function FleetOverviewPage() {
  // Placeholder demo data (API wiring comes next)
  const hiScore = 67

  const trendData = [
    { timestamp: "Mon", value: 72 },
    { timestamp: "Tue", value: 70 },
    { timestamp: "Wed", value: 68, isAnomaly: true },
    { timestamp: "Thu", value: 69 },
    { timestamp: "Fri", value: 67 },
  ]

  const fimData = [
    { name: "Fuel System", value: 38 },
    { name: "Cooling", value: 24 },
    { name: "Sensors", value: 18 },
    { name: "Electrical", value: 12 },
    { name: "Other", value: 8 },
  ]

  return (
    <>
      <NeonNavbar />

      <main className="max-w-7xl mx-auto px-6 py-10 space-y-10">
        {/* Hero */}
        <motion.section
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.4 }}
          className="space-y-2"
        >
          <h1 className="text-2xl font-semibold tracking-wide">
            Fleet Health Overview
          </h1>
          <p className="text-sm text-text-secondary">
            Real-time GenAI interpretation of predictive maintenance risk
            across the fleet.
          </p>
        </motion.section>

        {/* KPI Row */}
        <motion.section
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-3 gap-6"
        >
          <motion.div variants={staggerItem}>
            <HiGauge value={hiScore} />
          </motion.div>

          <motion.div variants={staggerItem} className="md:col-span-2">
            <TrendChart
              title="Fleet Health Trend"
              data={trendData}
            />
          </motion.div>
        </motion.section>

        {/* Distribution */}
        <motion.section
          variants={staggerContainer}
          initial="hidden"
          animate="visible"
          className="grid grid-cols-1 md:grid-cols-2 gap-6"
        >
          <motion.div variants={staggerItem}>
            <FimPieChart
              title="Failure Impact Distribution"
              data={fimData}
            />
          </motion.div>

          <motion.div
            variants={staggerItem}
            className="panel panel-glow p-6 space-y-4"
          >
            <h3 className="text-sm tracking-wide text-text-secondary">
              Executive Summary
            </h3>

            <p className="text-sm leading-relaxed text-text-primary">
              Fleet health remains moderately stable, with emerging risk
              signals concentrated in fuel system components. GenAI
              interpretation recommends targeted inspections for a
              subset of vehicles to prevent escalation.
            </p>

            <div className="divider" />

            <p className="text-xs text-text-muted">
              Last updated: just now · Model v1.0.0
            </p>
          </motion.div>
        </motion.section>
      </main>
    </>
  )
}
