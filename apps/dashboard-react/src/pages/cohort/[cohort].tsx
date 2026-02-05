import { useRouter } from "next/router"
import { useEffect, useState } from "react"
import { motion } from "framer-motion"

import NeonNavbar from "../../components/NeonNavbar"
import HiGauge from "../../components/HiGauge"
import TrendChart from "../../components/TrendChart"
import FimPieChart from "../../components/FimPieChart"

import { staggerContainer, staggerItem } from "../../theme/animations"
import {
  fetchCohortInterpretation,
  CohortInterpretation,
} from "../../services/apiClient"

export default function CohortDetailPage() {
  const router = useRouter()
  const { cohort } = router.query

  const [data, setData] = useState<CohortInterpretation | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!cohort || typeof cohort !== "string") return

    setLoading(true)
    setError(null)

    fetchCohortInterpretation(cohort)
      .then(setData)
      .catch(() =>
        setError("Failed to load cohort interpretation.")
      )
      .finally(() => setLoading(false))
  }, [cohort])

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

        {/* Loading / Error */}
        {loading && (
          <div className="panel p-6 text-sm text-text-secondary">
            Loading cohort interpretation…
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
                <HiGauge
                  value={
                    data.risk_distribution?.LOW
                      ? 100 - data.risk_distribution.HIGH * 2
                      : 60
                  }
                />
              </motion.div>

              <motion.div
                variants={staggerItem}
                className="md:col-span-2"
              >
                <TrendChart
                  title="Cohort Health Trend"
                  data={[]} // trend endpoint can plug here
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
                  data={
                    data.metrics.map((m) => ({
                      name: m.name,
                      value: m.value,
                    })) ?? []
                  }
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
                  {data.summary}
                </p>

                <div className="divider" />

                <p className="text-xs text-text-muted">
                  Model version: {data.model_version}
                </p>
              </motion.div>
            </motion.section>
          </>
        )}
      </main>
    </>
  )
}
