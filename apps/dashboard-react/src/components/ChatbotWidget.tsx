import { useMemo, useState } from "react"
import { AnimatePresence, motion } from "framer-motion"
import { MessageCircle, Send, X } from "lucide-react"

import { fetchChatReply } from "../services/apiClient"

interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

interface ChatbotWidgetProps {
  context?: Record<string, unknown>
}

export default function ChatbotWidget({ context }: ChatbotWidgetProps) {
  const [open, setOpen] = useState(false)
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      role: "assistant",
      content:
        "Ask about risk drivers, evidence, or recommended actions for this context.",
    },
  ])

  const placeholder = useMemo(() => {
    if (context?.vin) return "Explain this VIN risk..."
    if (context?.cohort_id) return "Explain this cohort anomaly pattern..."
    return "Ask about predictive telemetry..."
  }, [context])

  async function onSend() {
    const trimmed = input.trim()
    if (!trimmed || loading) return

    setMessages((prev) => [...prev, { role: "user", content: trimmed }])
    setInput("")
    setLoading(true)

    try {
      const reply = await fetchChatReply({
        message: trimmed,
        context,
      })
      setMessages((prev) => [...prev, { role: "assistant", content: reply }])
    } catch {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Unable to generate a reply right now. Please retry after the API is reachable.",
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button
        onClick={() => setOpen(true)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-full border border-neon-cyan/40 bg-bg-panel shadow-neonCyan flex items-center justify-center hover-lift"
        aria-label="Open explainability chat"
      >
        <MessageCircle size={20} className="text-neon-cyan" />
      </button>

      <AnimatePresence>
        {open && (
          <motion.section
            initial={{ opacity: 0, y: 30, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 24, scale: 0.95 }}
            transition={{ duration: 0.22 }}
            className="fixed bottom-24 right-6 z-50 w-[22rem] max-w-[92vw] h-[30rem] panel panel-glow flex flex-col"
          >
            <div className="px-4 py-3 border-b border-neon-cyan/20 flex items-center justify-between">
              <div>
                <div className="text-kicker">Agent Chat</div>
                <div className="text-sm text-neon-cyan">Explainability Assistant</div>
              </div>
              <button onClick={() => setOpen(false)} aria-label="Close chat">
                <X size={16} className="text-text-secondary hover:text-text-primary" />
              </button>
            </div>

            <div className="flex-1 overflow-y-auto px-4 py-3 space-y-3 text-sm">
              {messages.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={message.role === "assistant" ? "text-left" : "text-right"}
                >
                  <span
                    className={
                      message.role === "assistant"
                        ? "inline-block rounded-lg px-3 py-2 bg-neon-cyan/10 border border-neon-cyan/25 text-text-primary"
                        : "inline-block rounded-lg px-3 py-2 bg-neon-orange/12 border border-neon-orange/30 text-text-primary"
                    }
                  >
                    {message.content}
                  </span>
                </div>
              ))}
              {loading && <div className="text-neon-cyan animate-pulse">Generating response...</div>}
            </div>

            <div className="p-3 border-t border-neon-cyan/20 flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder={placeholder}
                className="flex-1 rounded-lg bg-bg-secondary border border-neon-cyan/25 px-3 py-2 text-sm outline-none focus:border-neon-cyan/60"
                onKeyDown={(event) => {
                  if (event.key === "Enter") {
                    void onSend()
                  }
                }}
              />
              <button
                onClick={() => void onSend()}
                className="rounded-lg bg-neon-cyan text-bg-primary px-3 py-2 disabled:opacity-60"
                disabled={loading}
              >
                <Send size={14} />
              </button>
            </div>
          </motion.section>
        )}
      </AnimatePresence>
    </>
  )
}

