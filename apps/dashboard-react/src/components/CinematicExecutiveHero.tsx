import Link from "next/link"
import dynamic from "next/dynamic"
import { motion } from "framer-motion"
import { ArrowRight, Clapperboard, Sparkles, ToggleLeft, ToggleRight } from "lucide-react"

const CinematicTelemetryScene = dynamic(
  () => import("./CinematicTelemetryScene"),
  { ssr: false }
)

interface CinematicExecutiveHeroProps {
  averageScore: number
  loading: boolean
  error: string | null
  cinematicMode: boolean
  onToggleCinematic: () => void
}

export default function CinematicExecutiveHero({
  averageScore,
  loading,
  error,
  cinematicMode,
  onToggleCinematic,
}: CinematicExecutiveHeroProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="panel panel-glow p-6 md:p-7 relative overflow-hidden min-h-[20rem]"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-neon-cyan/10 via-transparent to-neon-orange/8" />
      <div className="absolute inset-0">
        <CinematicTelemetryScene
          healthScore={averageScore || 58}
          cinematicMode={cinematicMode}
        />
      </div>
      <div className="absolute inset-0 bg-gradient-to-r from-bg-primary/90 via-bg-primary/70 to-bg-primary/40" />

      <div className="relative z-10 max-w-3xl space-y-4">
        <div className="flex flex-wrap items-center gap-2">
          <span className="chip-cyan">
            <Clapperboard size={12} className="mr-1.5" />
            Executive Presentation Mode
          </span>
          <span className="chip-amber">
            <Sparkles size={12} className="mr-1.5" />
            Next.js + Motion + R3F + ECharts
          </span>
        </div>

        <h1 className="text-3xl md:text-4xl leading-tight max-w-3xl">
          Telemetry decisions, staged as a cinematic control-room narrative.
        </h1>
        <p className="text-text-secondary max-w-2xl">
          Demonstrates explainable vehicle risk intelligence with real-time visual language tuned for leadership readouts and operational action packs.
        </p>

        <div className="flex flex-wrap items-center gap-3 pt-1">
          <Link href="/vin/WVWZZZ1KZ6W000001" className="chip-amber">
            Open VIN Intelligence <ArrowRight size={14} className="ml-1" />
          </Link>
          <Link href="/cohort/EURO6-DIESEL" className="chip-mint">
            Open Cohort Intelligence <ArrowRight size={14} className="ml-1" />
          </Link>
          <button
            type="button"
            onClick={onToggleCinematic}
            className="chip border-neon-cyan/35 bg-bg-secondary/70 text-neon-cyan hover:border-neon-cyan/60 transition-colors"
          >
            {cinematicMode ? (
              <ToggleRight size={14} className="mr-1.5" />
            ) : (
              <ToggleLeft size={14} className="mr-1.5" />
            )}
            {cinematicMode ? "Cinematic ON" : "Cinematic OFF"}
          </button>
        </div>

        <div className="flex flex-wrap gap-4 text-sm text-text-secondary">
          <div>
            Live health score:
            <span className="ml-2 text-neon-cyan font-display">{averageScore || 0}</span>
          </div>
          <div>{loading ? "Telemetry refresh in progress..." : "Telemetry synchronized"}</div>
        </div>

        {error && <p className="text-sm text-danger">{error}</p>}
      </div>
    </motion.section>
  )
}
