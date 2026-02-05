import type { AppProps } from "next/app"
import { AnimatePresence, motion } from "framer-motion"

import "../styles/globals.css"

export default function App({ Component, pageProps, router }: AppProps) {
  return (
    <AnimatePresence mode="wait">
      <motion.div
        key={router.route}
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -12 }}
        transition={{
          duration: 0.35,
          ease: "easeOut",
        }}
        className="
          min-h-screen
          bg-bg-primary
          text-text-primary
          relative
          overflow-x-hidden
        "
      >
        {/* Cinematic background layers */}
        <div className="pointer-events-none fixed inset-0 -z-10">
          {/* Ambient radial glow */}
          <div className="absolute inset-0 bg-radial-glow opacity-70" />

          {/* Subtle grid texture */}
          <div
            className="
              absolute inset-0
              bg-grid-fade
              bg-[size:40px_40px]
              opacity-[0.15]
            "
          />

          {/* Vignette */}
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/40" />
        </div>

        {/* Page content */}
        <Component {...pageProps} />
      </motion.div>
    </AnimatePresence>
  )
}
