import { motion } from "framer-motion"

import { getRiskStyle } from "../theme/neonTheme"

interface HiGaugeProps {
  value: number
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
    <section className="panel panel-glow p-5 h-full">
      <div className="text-kicker">Health Index</div>
      <h3 className="text-base">Predicted Stability</h3>
      <div className="mt-4 flex flex-col items-center gap-3">
        <div className="relative w-52 h-28 overflow-hidden">
          <div className={`absolute inset-0 rounded-t-full border-t-4 border-l-4 border-r-4 ${style.border}`} />
          <motion.div
            initial={{ rotate: -90 }}
            animate={{ rotate: rotation }}
            transition={{ duration: 0.8, ease: "easeOut" }}
            className="absolute bottom-0 left-1/2 origin-bottom"
            style={{ height: "92%" }}
          >
            <div className={`w-1.5 h-full ${style.bg} ${style.glow}`} />
          </motion.div>
        </div>
        <div className={`text-4xl font-display ${style.text}`}>{clamped.toFixed(0)}</div>
        <div className="chip-amber">Risk: {risk}</div>
      </div>
    </section>
  )
}

