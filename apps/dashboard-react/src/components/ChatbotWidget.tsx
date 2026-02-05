import { useState } from "react"
import { motion, AnimatePresence } from "framer-motion"
import { MessageCircle, X, Send } from "lucide-react"
import axios from "axios"

interface ChatMessage {
  role: "user" | "assistant"
  content: string
}

export default function ChatbotWidget() {
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)

  async function sendMessage() {
    if (!input.trim()) return

    const userMsg: ChatMessage = { role: "user", content: input }
    setMessages((m) => [...m, userMsg])
    setInput("")
    setLoading(true)

    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/chat`,
        { message: userMsg.content }
      )

      const assistantMsg: ChatMessage = {
        role: "assistant",
        content: res.data.reply,
      }

      setMessages((m) => [...m, assistantMsg])
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "Sorry — I couldn’t generate an explanation right now.",
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      {/* Floating button */}
      <button
        onClick={() => setOpen(true)}
        className="
          fixed bottom-6 right-6 z-50
          w-14 h-14 rounded-full
          bg-neon-purple shadow-neonPurple
          flex items-center justify-center
          hover:scale-105 transition
        "
      >
        <MessageCircle />
      </button>

      {/* Chat window */}
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 40 }}
            transition={{ duration: 0.3 }}
            className="
              fixed bottom-24 right-6 z-50
              w-96 h-[520px]
              panel panel-glow
              flex flex-col
            "
          >
            {/* Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-neon-purple/20">
              <span className="text-sm text-neon-purple">
                GenAI Interpreter
              </span>
              <button onClick={() => setOpen(false)}>
                <X size={16} />
              </button>
            </div>

            {/* Messages */}
            <div className="flex-1 p-4 space-y-3 overflow-y-auto text-sm">
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={
                    m.role === "user"
                      ? "text-right"
                      : "text-left text-neon-cyan"
                  }
                >
                  <span className="inline-block max-w-[80%]">
                    {m.content}
                  </span>
                </div>
              ))}

              {loading && (
                <div className="text-neon-purple animate-pulse">
                  Thinking…
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-3 border-t border-neon-purple/20 flex gap-2">
              <input
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about this data…"
                className="
                  flex-1 bg-bg-secondary
                  rounded-md px-3 py-2 text-sm
                  outline-none
                "
                onKeyDown={(e) => e.key === "Enter" && sendMessage()}
              />
              <button
                onClick={sendMessage}
                className="
                  bg-neon-cyan text-black
                  rounded-md px-3
                "
              >
                <Send size={14} />
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
