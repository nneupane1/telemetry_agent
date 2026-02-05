/**
 * Neon Theme System
 *
 * Central semantic mapping between domain meaning
 * (risk, severity, status) and visual representation.
 */

export type RiskLevel = "LOW" | "ELEVATED" | "HIGH" | "CRITICAL"

export interface NeonStyle {
  text: string
  border: string
  glow: string
  bg: string
}

/**
 * Risk → visual mapping
 * These tokens are consumed by components,
 * never hardcoded.
 */
export const riskTheme: Record<RiskLevel, NeonStyle> = {
  LOW: {
    text: "text-success",
    border: "border-success/40",
    glow: "shadow-neonGreen",
    bg: "bg-success/10",
  },
  ELEVATED: {
    text: "text-neon-orange",
    border: "border-warning/40",
    glow: "shadow-[0_0_16px_rgba(255,176,32,0.4)]",
    bg: "bg-warning/10",
  },
  HIGH: {
    text: "text-danger",
    border: "border-danger/50",
    glow: "shadow-[0_0_18px_rgba(255,79,79,0.55)]",
    bg: "bg-danger/10",
  },
  CRITICAL: {
    text: "text-neon-pink",
    border: "border-neon-pink/60",
    glow: "shadow-neonPink",
    bg: "bg-neon-pink/10",
  },
}

/**
 * Utility helper to safely resolve risk styles.
 */
export function getRiskStyle(
  level?: string
): NeonStyle {
  if (!level) return riskTheme.LOW
  return riskTheme[level as RiskLevel] ?? riskTheme.LOW
}
