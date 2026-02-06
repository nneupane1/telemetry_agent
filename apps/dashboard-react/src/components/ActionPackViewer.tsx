import { motion } from "framer-motion"
import { AlertTriangle, ShieldAlert, Sparkles } from "lucide-react"

import { getRiskStyle } from "../theme/neonTheme"

interface EvidenceItem {
  signal_code: string
  signal_description: string
  confidence: number
}

interface Recommendation {
  title: string
  rationale: string
  urgency: "LOW" | "MEDIUM" | "HIGH"
  suggested_action?: string
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
    <section className="panel panel-glow p-6 space-y-6">
      <div>
        <div className="text-kicker">Action Pack</div>
        <h2 className="text-xl">{title}</h2>
        <p className="mt-2 text-sm text-text-secondary leading-relaxed">{executiveSummary}</p>
      </div>

      <div className="divider" />

      <div className="space-y-4">
        {recommendations.length === 0 && (
          <div className="panel p-4 text-sm text-text-secondary">
            No active recommendations for this subject.
          </div>
        )}

        {recommendations.map((recommendation, index) => {
          const visual = getRiskStyle(recommendation.urgency === "HIGH" ? "HIGH" : "ELEVATED")

          return (
            <motion.article
              key={`${recommendation.title}-${index}`}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.06 }}
              className={`rounded-xl border ${visual.border} ${visual.bg} p-4`}
            >
              <div className="flex items-start gap-3">
                {recommendation.urgency === "HIGH" ? (
                  <ShieldAlert className={visual.text} size={20} />
                ) : (
                  <Sparkles className={visual.text} size={20} />
                )}
                <div className="flex-1 space-y-2">
                  <div className="flex flex-wrap items-center justify-between gap-2">
                    <h3 className={`font-display text-base ${visual.text}`}>{recommendation.title}</h3>
                    <span className={`chip ${visual.border} ${visual.text}`}>{recommendation.urgency}</span>
                  </div>
                  <p className="text-sm text-text-secondary">{recommendation.rationale}</p>
                  {recommendation.suggested_action && (
                    <p className="text-sm text-text-primary">
                      <AlertTriangle size={14} className="inline mr-1 text-neon-orange" />
                      {recommendation.suggested_action}
                    </p>
                  )}

                  {recommendation.evidence.length > 0 && (
                    <div className="flex flex-wrap gap-2 pt-1">
                      {recommendation.evidence.map((evidence, evIndex) => (
                        <span
                          key={`${evidence.signal_code}-${evIndex}`}
                          className="chip-cyan"
                          title={evidence.signal_description}
                        >
                          {evidence.signal_code} {Math.round(evidence.confidence * 100)}%
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </motion.article>
          )
        })}
      </div>
    </section>
  )
}

