import Link from "next/link"
import { motion } from "framer-motion"
import { Activity, CircleDot, Layers3, Truck } from "lucide-react"

export default function NeonNavbar() {
  return (
    <header className="sticky top-0 z-50 backdrop-blur-md bg-bg-secondary/70 border-b border-neon-cyan/20">
      <div className="max-w-7xl mx-auto px-6 py-4 flex flex-wrap items-center justify-between gap-3">
        <Link href="/" className="flex items-center gap-3">
          <motion.div
            animate={{ scale: [1, 1.12, 1] }}
            transition={{ repeat: Infinity, duration: 2.4 }}
            className="w-3 h-3 rounded-full bg-neon-cyan shadow-neonCyan"
          />
          <div>
            <div className="text-kicker">Predictive Interpreter</div>
            <div className="font-display text-base text-text-primary">Telemetry Command Center</div>
          </div>
        </Link>

        <nav className="flex items-center gap-2 text-sm">
          <NavItem href="/" icon={<Activity size={15} />} label="Overview" />
          <NavItem href="/vin/WVWZZZ1KZ6W000001" icon={<Truck size={15} />} label="VIN Lab" />
          <NavItem href="/cohort/EURO6-DIESEL" icon={<Layers3 size={15} />} label="Cohort Lab" />
        </nav>

        <div className="chip-cyan">
          <CircleDot size={13} className="mr-1.5" />
          Live Explainability
        </div>
      </div>
    </header>
  )
}

function NavItem({
  href,
  icon,
  label,
}: {
  href: string
  icon: React.ReactNode
  label: string
}) {
  return (
    <Link
      href={href}
      className="inline-flex items-center gap-2 px-3 py-2 rounded-lg border border-transparent hover:border-neon-cyan/40 hover:bg-neon-cyan/10 text-text-secondary hover:text-neon-cyan transition-colors"
    >
      {icon}
      <span>{label}</span>
    </Link>
  )
}

