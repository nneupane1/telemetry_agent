import { useRouter } from "next/router"
import { useEffect, useState } from "react"
import { motion } from "framer-motion"

import NeonNavbar from "../../components/NeonNavbar"
import HiGauge from "../../components/HiGauge"
import TrendChart from "../../components/TrendChart"
import ActionPackViewer from "../../components/ActionPackViewer"

import { staggerContainer, staggerItem } from "../../theme/animations"
import {
  fetchVinInterpretation,
  VinInterpretation,
} from "../../services/apiClient"

export default function VinDetailPage() {
  const router = useRouter()
  const { vin } = router.query

  const [data, setData] = useState<VinInterpretation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!vin || typeof vin !== "string") return

    setLoading(true)
    setError(null)

    fetchVinInterpretation(vin)
      .then(setData)
      .catch(() =>
        setError("Failed to load VIN interpretation. Please try again.")
      )
      .finally(() => setLoading(false))
  }, [vin])

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

        {/* Loading / Error */}
        {loading && (
          <div className="panel p-6 text-sm text-text-secondary">
            Loading VIN interpretation…
          </div>
        )}

        {error && (
          <div className="panel p-6 text-sm text-danger">
            {error}
          </div>
        )}

        {/* Content */}
        {data && (
          <>
            {/* KPIs */}
            <motion.section
              variants={staggerContainer}
              initial="hidden"
              animate="visible"
              className="grid grid-cols-1 md:grid-cols-3 gap-6"
            >
              <motion.div variants={staggerItem}>
                <HiGauge value={data.recommendations.length * 15} />
              </motion.div>

              <motion.div
                variants={staggerItem}
                className="md:col-span-2"
              >
                <TrendChart
                  title="VIN Health Trend"
                  data={[]} // backend trend endpoint can plug in here
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
                  title="Recommended Actions"
                  executiveSummary={data.summary}
                  recommendations={data.recommendations}
                />
              </motion.div>
            </motion.section>

            {/* Metadata */}
            <div className="text-xs text-text-muted">
              Model version: {data.model_version}
            </div>
          </>
        )}
      </main>
    </>
  )
}
