import { useState } from "react"
import { motion } from "framer-motion"
import { Download, FileText, RefreshCcw } from "lucide-react"
import axios from "axios"

interface PdfExportPanelProps {
  subjectType: "vin" | "cohort"
  subjectId: string
  title?: string
}

export default function PdfExportPanel({
  subjectType,
  subjectId,
  title = "Export Report",
}: PdfExportPanelProps) {
  const [loading, setLoading] = useState(false)
  const [pdfUrl, setPdfUrl] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function generatePdf() {
    setLoading(true)
    setError(null)

    try {
      const res = await axios.post(
        `${process.env.NEXT_PUBLIC_API_BASE_URL}/export/pdf`,
        { subject_type: subjectType, subject_id: subjectId },
        { responseType: "blob" }
      )

      const blob = new Blob([res.data], { type: "application/pdf" })
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
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.3 }}
      className="panel panel-glow p-6 space-y-4"
    >
      {/* Header */}
      <div className="flex items-center gap-2">
        <FileText className="text-neon-purple" size={18} />
        <h3 className="text-sm font-medium">{title}</h3>
      </div>

      {/* Actions */}
      <div className="flex items-center gap-3">
        <button
          onClick={generatePdf}
          disabled={loading}
          className="
            flex items-center gap-2
            px-3 py-2 rounded-md text-sm
            bg-neon-purple text-black
            hover:opacity-90 transition
          "
        >
          <RefreshCcw size={14} />
          {loading ? "Generating…" : "Generate PDF"}
        </button>

        {pdfUrl && (
          <a
            href={pdfUrl}
            download={`${subjectType}-${subjectId}.pdf`}
            className="
              flex items-center gap-2
              px-3 py-2 rounded-md text-sm
              bg-bg-secondary border border-neon-purple/30
              hover:text-neon-cyan transition
            "
          >
            <Download size={14} />
            Download
          </a>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="text-sm text-danger">
          {error}
        </div>
      )}

      {/* Preview */}
      {pdfUrl && (
        <iframe
          src={pdfUrl}
          className="w-full h-[420px] rounded-md border border-neon-purple/20"
        />
      )}
    </motion.section>
  )
}
