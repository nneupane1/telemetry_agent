import axios, { AxiosInstance } from "axios"

// ------------------------------------------------------------
// Configuration
// ------------------------------------------------------------

const BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000"

const CHAT_WS_URL =
  process.env.NEXT_PUBLIC_CHAT_WS_URL ||
  toWebSocketUrl(`${BASE_URL}/chat/ws`)

const CHAT_REST_LATENCY_THRESHOLD_MS = parsePositiveInt(
  process.env.NEXT_PUBLIC_CHAT_REST_LATENCY_THRESHOLD_MS,
  1200
)

const CHAT_REST_BREACH_LIMIT = parsePositiveInt(
  process.env.NEXT_PUBLIC_CHAT_REST_BREACH_LIMIT,
  3
)

const CHAT_WS_TIMEOUT_MS = parsePositiveInt(
  process.env.NEXT_PUBLIC_CHAT_WS_TIMEOUT_MS,
  15000
)

// ------------------------------------------------------------
// Axios instance
// ------------------------------------------------------------

const api: AxiosInstance = axios.create({
  baseURL: BASE_URL,
  timeout: 15000,
  headers: {
    "Content-Type": "application/json",
  },
})

function parsePositiveInt(raw: string | undefined, fallback: number): number {
  const parsed = Number(raw)
  if (!Number.isFinite(parsed) || parsed <= 0) {
    return fallback
  }
  return Math.floor(parsed)
}

function toWebSocketUrl(rawUrl: string): string {
  const normalized = rawUrl.replace(/\/+$/, "")
  if (normalized.startsWith("https://")) {
    return normalized.replace(/^https:\/\//, "wss://")
  }
  if (normalized.startsWith("http://")) {
    return normalized.replace(/^http:\/\//, "ws://")
  }
  if (normalized.startsWith("ws://") || normalized.startsWith("wss://")) {
    return normalized
  }
  return `ws://${normalized}`
}

function browserWebSocketAvailable(): boolean {
  return typeof window !== "undefined" && typeof window.WebSocket !== "undefined"
}

type ChatPayload = {
  message: string
  context?: Record<string, unknown>
}

type PendingRequest = {
  resolve: (value: string) => void
  reject: (reason?: unknown) => void
  timeoutHandle: ReturnType<typeof setTimeout>
}

class ChatWebSocketTransport {
  private socket: WebSocket | null = null
  private connecting: Promise<void> | null = null
  private pending = new Map<string, PendingRequest>()

  async request(payload: ChatPayload): Promise<string> {
    await this.ensureConnected()
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error("WebSocket is not connected")
    }

    const requestId = `chat-${Date.now()}-${Math.random()
      .toString(36)
      .slice(2, 10)}`

    return new Promise<string>((resolve, reject) => {
      const timeoutHandle = setTimeout(() => {
        this.pending.delete(requestId)
        reject(new Error("WebSocket chat request timed out"))
      }, CHAT_WS_TIMEOUT_MS)

      this.pending.set(requestId, {
        resolve,
        reject,
        timeoutHandle,
      })

      this.socket?.send(
        JSON.stringify({
          message: payload.message,
          context: payload.context,
          request_id: requestId,
        })
      )
    })
  }

  private async ensureConnected(): Promise<void> {
    if (!browserWebSocketAvailable()) {
      throw new Error("WebSocket transport is unavailable in this runtime")
    }

    if (this.socket && this.socket.readyState === WebSocket.OPEN) {
      return
    }

    if (this.connecting) {
      return this.connecting
    }

    this.connecting = new Promise<void>((resolve, reject) => {
      const socket = new WebSocket(CHAT_WS_URL)

      const cleanup = () => {
        socket.onopen = null
        socket.onerror = null
      }

      socket.onopen = () => {
        cleanup()
        this.socket = socket
        resolve()
      }

      socket.onerror = () => {
        cleanup()
        reject(new Error("Unable to establish chat WebSocket connection"))
      }

      socket.onmessage = (event) => {
        this.handleMessage(event.data)
      }

      socket.onclose = () => {
        if (this.socket === socket) {
          this.socket = null
        }
        this.rejectAllPending("Chat WebSocket connection closed")
      }
    }).finally(() => {
      this.connecting = null
    })

    return this.connecting
  }

  private handleMessage(rawMessage: unknown): void {
    if (typeof rawMessage !== "string") {
      return
    }

    let payload: any
    try {
      payload = JSON.parse(rawMessage)
    } catch {
      return
    }

    const requestId = payload?.request_id
    if (typeof requestId !== "string") {
      return
    }

    const pending = this.pending.get(requestId)
    if (!pending) {
      return
    }

    this.pending.delete(requestId)
    clearTimeout(pending.timeoutHandle)

    if (payload?.type === "error") {
      pending.reject(new Error(payload?.detail || "WebSocket chat request failed"))
      return
    }

    if (typeof payload?.reply !== "string") {
      pending.reject(new Error("Invalid WebSocket chat response payload"))
      return
    }

    pending.resolve(payload.reply)
  }

  private rejectAllPending(message: string): void {
    this.pending.forEach((pending, requestId) => {
      clearTimeout(pending.timeoutHandle)
      pending.reject(new Error(`${message} (${requestId})`))
    })
    this.pending.clear()
  }
}

const chatWebSocketTransport = new ChatWebSocketTransport()
let chatRestBreachCount = 0
let preferChatWebSocket = false

function registerRestLatency(latencyMs: number): void {
  if (latencyMs > CHAT_REST_LATENCY_THRESHOLD_MS) {
    chatRestBreachCount += 1
    if (chatRestBreachCount >= CHAT_REST_BREACH_LIMIT) {
      preferChatWebSocket = true
    }
    return
  }
  chatRestBreachCount = 0
}

// ------------------------------------------------------------
// Domain types (aligned with backend models)
// ------------------------------------------------------------

export interface EvidenceItem {
  source_model: string
  signal_code: string
  signal_description: string
  confidence: number
  observed_at?: string
}

export interface Recommendation {
  title: string
  rationale: string
  urgency: "LOW" | "MEDIUM" | "HIGH"
  suggested_action?: string
  evidence: EvidenceItem[]
}

export interface VinInterpretation {
  vin: string
  summary: string
  risk_level: "LOW" | "ELEVATED" | "HIGH" | "CRITICAL"
  recommendations: Recommendation[]
  evidence_summary?: Record<string, Record<string, unknown>>
  model_version: string
}

export interface CohortMetric {
  name: string
  value: number
  unit?: string
  description?: string
}

export interface CohortAnomaly {
  title: string
  description: string
  affected_vin_count: number
  severity: string
  related_signals?: string[]
}

export interface CohortInterpretation {
  cohort_id: string
  summary: string
  metrics: CohortMetric[]
  anomalies: CohortAnomaly[]
  risk_distribution?: Record<string, number>
  model_version: string
}

export interface CohortListItem {
  cohort_id: string
  cohort_description?: string | null
}

// ------------------------------------------------------------
// API functions
// ------------------------------------------------------------

export async function fetchVinInterpretation(
  vin: string
): Promise<VinInterpretation> {
  const { data } = await api.get<VinInterpretation>(`/vin/${vin}`)
  return data
}

export async function fetchCohortInterpretation(
  cohortId: string
): Promise<CohortInterpretation> {
  const { data } = await api.get<CohortInterpretation>(
    `/cohort/${cohortId}`
  )
  return data
}

export async function fetchCohortList(): Promise<CohortListItem[]> {
  const { data } = await api.get<{ cohorts: CohortListItem[] }>(
    "/cohort/list"
  )
  return data.cohorts || []
}

export async function createActionPack(payload: {
  subject_type: string
  subject_id: string
  title: string
  executive_summary: string
  recommendations: Recommendation[]
}) {
  const { data } = await api.post("/action-pack", payload)
  return data
}

export async function fetchChatReply(payload: {
  message: string
  context?: Record<string, unknown>
}) {
  if (preferChatWebSocket) {
    try {
      return await chatWebSocketTransport.request(payload)
    } catch {
      preferChatWebSocket = false
      chatRestBreachCount = 0
    }
  }

  const startedAt = Date.now()
  try {
    const { data } = await api.post<{ reply: string }>("/chat", payload)
    registerRestLatency(Date.now() - startedAt)
    return data.reply
  } catch (restError) {
    if (!browserWebSocketAvailable()) {
      throw restError
    }

    try {
      const fallbackReply = await chatWebSocketTransport.request(payload)
      preferChatWebSocket = true
      return fallbackReply
    } catch {
      throw restError
    }
  }
}

export async function exportPdf(payload: {
  subject_type: "vin" | "cohort"
  subject_id: string
}) {
  const { data } = await api.post<ArrayBuffer>("/export/pdf", payload, {
    responseType: "arraybuffer",
  })
  return data
}

export async function recordApproval(payload: {
  subject_type: string
  subject_id: string
  decision: "approve" | "reject" | "escalate"
  comment: string
  decided_by?: string
}) {
  const { data } = await api.post("/approval", payload)
  return data
}
