export function toPercent(value: number, digits = 0): string {
  return `${(value * 100).toFixed(digits)}%`
}

export function safeDate(value?: string): string {
  if (!value) return "n/a"
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleString()
}

export function titleCaseRisk(value: string): string {
  return value.toLowerCase().replace(/(^\\w|_\\w)/g, (token) => token.replace("_", " ").toUpperCase())
}

