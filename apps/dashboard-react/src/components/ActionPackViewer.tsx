import { motion } from "framer-motion"
import { AlertTriangle, CheckCircle } from "lucide-react"

import { getRiskStyle } from "../theme/neonTheme"
import { staggerContainer, staggerItem } from "../theme/animations"

interface EvidenceItem {
  signal_code: string
  signal_description: string
  confidence: number
}

interface Recommendation {
  title: string
  rationale: string
  urgency: "LOW" | "MEDIUM" | "HIGH"
  evidence: EvidenceItem[]
}

interface ActionPackViewerProps {
  title: string
  executiveSummary: string
  recommendations: Recommendation[]
}

export default function ActionPackViewer({
  title,
  executiveSummary,
  recommendations,
}: ActionPackViewerProps) {
  return (
    <motion.section
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="panel panel-glow p-6 space-y-6"
    >
      {/* Header */}
      <div>
        <h2 className="text-lg font-semibold text-neon-purple">
          {title}
        </h2>
        <p className="mt-2 text-sm text-text-secondary">
          {executiveSummary}
        </p>
      </div>

      <div className="divider" />

      {/* Recommendations */}
      <div className="space-y-4">
        {recommendations.map((rec, idx) => {
          const style = getRiskStyle(
            rec.urgency === "HIGH" ? "HIGH" : "ELEVATED"
          )

          return (
            <motion.div
              key={idx}
              variants={staggerItem}
              className={`
                rounded-lg border p-4
                ${style.border}
                ${style.bg}
              `}
            >
              <div className="flex items-start gap-3">
                {rec.urgency === "HIGH" ? (
                  <AlertTriangle
                    className={`mt-1 ${style.text}`}
                    size={18}
                  />
                ) : (
                  <CheckCircle
                    className={`mt-1 ${style.text}`}
                    size={18}
                  />
                )}

                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className={`font-medium ${style.text}`}>
                      {rec.title}
                    </h3>
                    <span
                      className={`
                        text-xs px-2 py-1 rounded-full
                        border ${style.border}
                        ${style.text}
                      `}
                    >
                      {rec.urgency}
                    </span>
                  </div>

                  <p className="mt-1 text-sm text-text-secondary">
                    {rec.rationale}
                  </p>

                  {/* Evidence */}
                  {rec.evidence.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {rec.evidence.map((ev, i) => (
                        <span
                          key={i}
                          className="
                            text-xs px-2 py-1 rounded-md
                            bg-bg-secondary
                            border border-neon-purple/20
                            text-text-muted
                          "
                        >
                          {ev.signal_code} ·{" "}
                          {Math.round(ev.confidence * 100)}%
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>
    </motion.section>
  )
}
