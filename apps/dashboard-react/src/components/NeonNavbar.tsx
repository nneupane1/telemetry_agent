import Link from "next/link"
import { motion } from "framer-motion"
import { Activity, Layers, Truck } from "lucide-react"

import { floatSlow } from "../theme/animations"

export default function NeonNavbar() {
  return (
    <motion.header
      variants={floatSlow}
      animate="animate"
      className="
        sticky top-0 z-50
        backdrop-blur-md
        bg-bg-secondary/70
        border-b border-neon-purple/20
      "
    >
      <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
        {/* Brand */}
        <Link href="/">
          <div className="flex items-center gap-3 cursor-pointer">
            <div className="w-3 h-3 rounded-full bg-neon-purple shadow-neonPurple animate-pulseGlow" />
            <span className="text-lg font-semibold tracking-wide text-neon-purple">
              GenAI Interpreter
            </span>
          </div>
        </Link>

        {/* Navigation */}
        <nav className="flex items-center gap-8 text-sm">
          <NavItem href="/" icon={<Activity size={16} />} label="Fleet" />
          <NavItem href="/cohort/demo" icon={<Layers size={16} />} label="Cohorts" />
          <NavItem href="/vin/demo" icon={<Truck size={16} />} label="VIN Explorer" />
        </nav>
      </div>
    </motion.header>
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
    <Link href={href}>
      <motion.div
        whileHover={{ y: -2 }}
        className="
          flex items-center gap-2
          text-text-secondary
          hover:text-neon-cyan
          transition-colors
          cursor-pointer
        "
      >
        {icon}
        <span className="tracking-wide">{label}</span>
      </motion.div>
    </Link>
  )
}
