import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts"
import { motion } from "framer-motion"

interface TrendPoint {
  timestamp: string
  value: number
  isAnomaly?: boolean
}

interface TrendChartProps {
  title: string
  data: TrendPoint[]
  color?: string
}

export default function TrendChart({
  title,
  data,
  color = "#9D7BFF",
}: TrendChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="panel panel-glow p-6"
    >
      <div className="mb-4 text-sm tracking-wide text-text-secondary">
        {title}
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer>
          <LineChart data={data}>
            <CartesianGrid
              stroke="rgba(255,255,255,0.05)"
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="timestamp"
              tick={{ fill: "#AAB0D6", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />

            <YAxis
              tick={{ fill: "#AAB0D6", fontSize: 11 }}
              axisLine={false}
              tickLine={false}
            />

            <Tooltip
              contentStyle={{
                backgroundColor: "#0E1428",
                border: "1px solid rgba(157,123,255,0.3)",
                borderRadius: "8px",
                color: "#E6E9F2",
              }}
            />

            <Line
              type="monotone"
              dataKey="value"
              stroke={color}
              strokeWidth={2}
              dot={false}
              isAnimationActive
            />

            {/* Anomaly dots */}
            <Line
              type="monotone"
              dataKey={(d) => (d.isAnomaly ? d.value : null)}
              stroke="transparent"
              dot={{
                r: 4,
                fill: "#FF4FD8",
                stroke: "#FF4FD8",
                strokeWidth: 1,
              }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  )
}
