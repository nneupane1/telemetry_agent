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
        transition={{ duration: 0.3, ease: "easeOut" }}
        className="min-h-screen text-text-primary relative overflow-x-hidden"
      >
        <div className="pointer-events-none fixed inset-0 -z-10">
          <div className="absolute inset-0 aurora-bg" />
          <div className="absolute inset-0 glass-grid opacity-20" />
          <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/45" />
        </div>
        <Component {...pageProps} />
      </motion.div>
    </AnimatePresence>
  )
}

