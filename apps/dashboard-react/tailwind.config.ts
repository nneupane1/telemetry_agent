import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: "class",
  content: [
    "./src/**/*.{ts,tsx}",
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}"
  ],
  theme: {
    extend: {
      colors: {
        bg: {
          primary: "#05070D",
          secondary: "#0A0F1F",
          panel: "#0E1428"
        },
        neon: {
          cyan: "#3CF2FF",
          purple: "#9D7BFF",
          pink: "#FF4FD8",
          green: "#2BFF88",
          orange: "#FF9F43"
        },
        text: {
          primary: "#E6E9F2",
          secondary: "#AAB0D6",
          muted: "#6C72A6"
        },
        danger: "#FF4F4F",
        warning: "#FFB020",
        success: "#2BFF88"
      },

      boxShadow: {
        neonCyan:
          "0 0 8px rgba(60,242,255,0.6), 0 0 24px rgba(60,242,255,0.35)",
        neonPurple:
          "0 0 8px rgba(157,123,255,0.6), 0 0 24px rgba(157,123,255,0.35)",
        neonPink:
          "0 0 8px rgba(255,79,216,0.6), 0 0 24px rgba(255,79,216,0.35)",
        neonGreen:
          "0 0 8px rgba(43,255,136,0.6), 0 0 24px rgba(43,255,136,0.35)"
      },

      backgroundImage: {
        "radial-glow":
          "radial-gradient(circle at top, rgba(157,123,255,0.15), transparent 60%)",
        "grid-fade":
          "linear-gradient(rgba(255,255,255,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.03) 1px, transparent 1px)"
      },

      animation: {
        pulseGlow: "pulseGlow 3s ease-in-out infinite",
        floatSlow: "floatSlow 6s ease-in-out infinite"
      },

      keyframes: {
        pulseGlow: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" }
        },
        floatSlow: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-8px)" }
        }
      }
    }
  },
  plugins: []
}

export default config
