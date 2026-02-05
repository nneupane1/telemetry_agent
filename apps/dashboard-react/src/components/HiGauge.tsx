import { motion } from "framer-motion"
import { getRiskStyle } from "../theme/neonTheme"

interface HiGaugeProps {
  value: number // 0–100
}

function getRiskFromValue(value: number) {
  if (value >= 80) return "LOW"
  if (value >= 60) return "ELEVATED"
  if (value >= 40) return "HIGH"
  return "CRITICAL"
}

export default function HiGauge({ value }: HiGaugeProps) {
  const clamped = Math.max(0, Math.min(100, value))
  const risk = getRiskFromValue(clamped)
  const style = getRiskStyle(risk)

  const rotation = (clamped / 100) * 180 - 90

  return (
    <div className="panel panel-glow p-6 flex flex-col items-center gap-4">
      <div className="text-sm tracking-wide text-text-secondary">
        Health Index
      </div>

      <div className="relative w-48 h-24 overflow-hidden">
        {/* Arc */}
        <div
          className={`
            absolute inset-0
            rounded-t-full
            border-t-4 border-l-4 border-r-4
            ${style.border}
          `}
        />

        {/* Needle */}
        <motion.div
          initial={{ rotate: -90 }}
          animate={{ rotate: rotation }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          className="absolute bottom-0 left-1/2 origin-bottom"
          style={{ height: "90%" }}
        >
          <div
            className={`
              w-1 h-full
              ${style.bg}
              ${style.glow}
            `}
          />
        </motion.div>
      </div>

      {/* Value */}
      <div className={`text-3xl font-semibold ${style.text}`}>
        {clamped.toFixed(0)}
      </div>

      <div className="text-xs text-text-muted tracking-wide">
        Risk Level: {risk}
      </div>
    </div>
  )
}
