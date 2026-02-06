import { motion } from "framer-motion"
import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts"

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
  color = "#42E5FF",
}: TrendChartProps) {
  return (
    <motion.section
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.28 }}
      className="panel panel-glow p-5"
    >
      <div className="text-kicker">Trend</div>
      <h3 className="text-base">{title}</h3>
      <div className="h-64 mt-4">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-sm text-text-muted border border-dashed border-neon-cyan/20 rounded-lg">
            No trend points available for this context.
          </div>
        ) : (
          <ResponsiveContainer>
            <LineChart data={data}>
              <CartesianGrid stroke="rgba(255,255,255,0.06)" strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tick={{ fill: "#9EC7D9", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <YAxis
                tick={{ fill: "#9EC7D9", fontSize: 11 }}
                axisLine={false}
                tickLine={false}
              />
              <Tooltip
                contentStyle={{
                  backgroundColor: "#102635",
                  border: "1px solid rgba(66,229,255,0.28)",
                  borderRadius: "10px",
                  color: "#E8F7FF",
                }}
              />
              <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2.5} dot={false} />
              <Line
                type="monotone"
                dataKey={(point) => (point.isAnomaly ? point.value : null)}
                stroke="transparent"
                dot={{ r: 4, fill: "#FF8C42", stroke: "#FF8C42", strokeWidth: 1 }}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>
    </motion.section>
  )
}

