import { motion } from "framer-motion"
import Link from "next/link"
import { ArrowRight } from "lucide-react"

import { getRiskStyle } from "../theme/neonTheme"
import { staggerContainer, staggerItem } from "../theme/animations"

interface VinItem {
  vin: string
  risk_level: "LOW" | "ELEVATED" | "HIGH" | "CRITICAL"
  hi_score: number
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
    <motion.section
      variants={staggerContainer}
      initial="hidden"
      animate="visible"
      className="panel panel-glow p-6 space-y-4"
    >
      <h3 className="text-sm tracking-wide text-text-secondary">
        {title}
      </h3>

      <div className="space-y-2">
        {vins.map((vinItem) => {
          const style = getRiskStyle(vinItem.risk_level)

          return (
            <motion.div
              key={vinItem.vin}
              variants={staggerItem}
              className={`
                flex items-center justify-between
                px-4 py-3 rounded-md
                border ${style.border}
                ${style.bg}
                hover-lift
              `}
            >
              {/* VIN info */}
              <div className="space-y-1">
                <div className="font-medium tracking-wide">
                  {vinItem.vin}
                </div>
                <div className="text-xs text-text-muted">
                  HI Score:{" "}
                  <span className={style.text}>
                    {vinItem.hi_score}
                  </span>{" "}
                  · Risk:{" "}
                  <span className={style.text}>
                    {vinItem.risk_level}
                  </span>
                </div>
              </div>

              {/* Navigate */}
              <Link href={`/vin/${vinItem.vin}`}>
                <motion.div
                  whileHover={{ x: 4 }}
                  className="
                    flex items-center gap-1
                    text-sm text-text-secondary
                    hover:text-neon-cyan
                    cursor-pointer
                  "
                >
                  View
                  <ArrowRight size={14} />
                </motion.div>
              </Link>
            </motion.div>
          )
        })}
      </div>
    </motion.section>
  )
}
