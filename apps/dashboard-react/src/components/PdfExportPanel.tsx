import { useEffect, useState } from "react"
import { motion } from "framer-motion"
import { Download, FileText, RefreshCcw } from "lucide-react"

import { exportPdf } from "../services/apiClient"

interface PdfExportPanelProps {
  subjectType: "vin" | "cohort"
  subjectId: string
  title?: string
}

export default function PdfExportPanel({
  subjectType,
  subjectId,
  title = "PDF Export",
}: PdfExportPanelProps) {
  const [loading, setLoading] = useState(false)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    return () => {
      if (pdfUrl) URL.revokeObjectURL(pdfUrl)
    }
  }, [pdfUrl])

  async function generatePdf() {
    setLoading(true)
    setError(null)
    try {
      const bytes = await exportPdf({
        subject_type: subjectType,
        subject_id: subjectId,
      })
      const blob = new Blob([bytes], { type: "application/pdf" })
      const url = URL.createObjectURL(blob)
      setPdfUrl(url)
    } catch {
      setError("Failed to generate PDF report.")
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.24 }}
      className="panel panel-glow p-5 space-y-4"
    >
      <div className="flex items-center gap-2">
        <FileText size={18} className="text-neon-cyan" />
        <h3 className="text-base">{title}</h3>
      </div>

      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => void generatePdf()}
          disabled={loading}
          className="inline-flex items-center gap-2 rounded-lg px-3 py-2 bg-neon-cyan text-bg-primary font-medium disabled:opacity-60"
        >
          <RefreshCcw size={14} />
          {loading ? "Generating..." : "Generate PDF"}
        </button>

        {pdfUrl && (
          <a
            href={pdfUrl}
            download={`${subjectType}-${subjectId}.pdf`}
            className="inline-flex items-center gap-2 rounded-lg px-3 py-2 border border-neon-cyan/35 hover:bg-neon-cyan/10 transition-colors"
          >
            <Download size={14} />
            Download
          </a>
        )}
      </div>

      {error && <p className="text-sm text-danger">{error}</p>}

      {pdfUrl && (
        <iframe
          src={pdfUrl}
          className="w-full h-[420px] rounded-lg border border-neon-cyan/25"
        />
      )}
    </motion.section>
  )
}

