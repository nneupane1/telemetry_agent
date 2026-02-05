import { Variants } from "framer-motion"

/**
 * Page-level transitions
 */
export const pageTransition: Variants = {
  initial: {
    opacity: 0,
    y: 12,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.35,
      ease: "easeOut",
    },
  },
  exit: {
    opacity: 0,
    y: -12,
    transition: {
      duration: 0.25,
      ease: "easeIn",
    },
  },
}

/**
 * Generic panel / card entrance
 */
export const panelEntrance: Variants = {
  hidden: {
    opacity: 0,
    y: 16,
    scale: 0.98,
  },
  visible: (delay = 0) => ({
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      delay,
      duration: 0.4,
      ease: "easeOut",
    },
  }),
}

/**
 * Staggered container for lists / grids
 */
export const staggerContainer: Variants = {
  hidden: {},
  visible: {
    transition: {
      staggerChildren: 0.08,
      delayChildren: 0.05,
    },
  },
}

/**
 * Item used inside staggered containers
 */
export const staggerItem: Variants = {
  hidden: {
    opacity: 0,
    y: 10,
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3,
      ease: "easeOut",
    },
  },
}

/**
 * Subtle pulsing glow (alerts, live indicators)
 */
export const pulseGlow: Variants = {
  animate: {
    opacity: [0.6, 1, 0.6],
    transition: {
      duration: 2.5,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
}

/**
 * Floating effect (background elements, hero accents)
 */
export const floatSlow: Variants = {
  animate: {
    y: [0, -8, 0],
    transition: {
      duration: 6,
      repeat: Infinity,
      ease: "easeInOut",
    },
  },
}
