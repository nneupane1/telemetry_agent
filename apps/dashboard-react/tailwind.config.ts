import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: ["./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#061017",
          secondary: "#0c1e2a",
          panel: "#102635",
        },
        neon: {
          cyan: "#42E5FF",
          purple: "#53C8D8",
          pink: "#FFB347",
          green: "#7CF7A5",
          orange: "#FF8C42",
        },
        text: {
          primary: "#E8F7FF",
          secondary: "#9EC7D9",
          muted: "#6F97AB",
        },
        danger: "#FF5C5C",
        warning: "#FFB347",
        success: "#7CF7A5",
      },
      boxShadow: {
        neonCyan:
          "0 0 12px rgba(66,229,255,0.45), 0 0 30px rgba(66,229,255,0.24)",
        neonPurple:
          "0 0 12px rgba(83,200,216,0.4), 0 0 28px rgba(83,200,216,0.22)",
        neonPink:
          "0 0 12px rgba(255,179,71,0.4), 0 0 28px rgba(255,179,71,0.24)",
        neonGreen:
          "0 0 12px rgba(124,247,165,0.45), 0 0 28px rgba(124,247,165,0.25)",
      },
      backgroundImage: {
        atmosphere:
          "radial-gradient(circle at 14% 18%, rgba(66,229,255,0.2), transparent 38%), radial-gradient(circle at 88% 10%, rgba(255,140,66,0.22), transparent 35%), radial-gradient(circle at 50% 100%, rgba(124,247,165,0.13), transparent 52%)",
        grid:
          "linear-gradient(rgba(255,255,255,0.035) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.035) 1px, transparent 1px)",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Manrope'", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      animation: {
        pulseGlow: "pulseGlow 3s ease-in-out infinite",
        floatSlow: "floatSlow 6s ease-in-out infinite",
      },
      keyframes: {
        pulseGlow: {
          "0%, 100%": { opacity: "0.55" },
          "50%": { opacity: "1" },
        },
        floatSlow: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-9px)" },
        },
      },
    },
  },
  plugins: [],
}

export default config

