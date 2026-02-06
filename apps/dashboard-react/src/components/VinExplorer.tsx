import Link from "next/link"
import { motion } from "framer-motion"
import { ArrowRight, Radar } from "lucide-react"

import { getRiskStyle } from "../theme/neonTheme"

interface VinItem {
  vin: string
  risk_level: "LOW" | "ELEVATED" | "HIGH" | "CRITICAL"
  hi_score: number
  summary?: string
}

interface VinExplorerProps {
  title?: string
  vins: VinItem[]
}

export default function VinExplorer({
  title = "Vehicle Explorer",
  vins,
}: VinExplorerProps) {
  return (
    <section className="panel panel-glow p-5 space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <div className="text-kicker">VIN Drilldown</div>
          <h3 className="text-base">{title}</h3>
        </div>
        <div className="chip-cyan">
          <Radar size={13} className="mr-1.5" />
          {vins.length} VINs
        </div>
      </div>

      <div className="space-y-2">
        {vins.map((vinItem, index) => {
          const style = getRiskStyle(vinItem.risk_level)
          return (
            <motion.article
              key={vinItem.vin}
              initial={{ opacity: 0, y: 8 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.04 }}
              className={`rounded-lg border ${style.border} ${style.bg} px-4 py-3 hover-lift`}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-1">
                  <div className="font-display text-base">{vinItem.vin}</div>
                  <div className="text-xs text-text-muted">
                    HI Score <span className={style.text}>{vinItem.hi_score}</span> | Risk{" "}
                    <span className={style.text}>{vinItem.risk_level}</span>
                  </div>
                  {vinItem.summary && (
                    <p className="text-xs text-text-secondary max-w-xl">{vinItem.summary}</p>
                  )}
                </div>
                <Link
                  href={`/vin/${vinItem.vin}`}
                  className="inline-flex items-center gap-1 text-sm text-neon-cyan hover:underline"
                >
                  Open <ArrowRight size={14} />
                </Link>
              </div>
            </motion.article>
          )
        })}
      </div>
    </section>
  )
}

