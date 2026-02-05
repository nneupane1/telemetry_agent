import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts"
import { motion } from "framer-motion"

interface FimSlice {
  name: string
  value: number
}

interface FimPieChartProps {
  title: string
  data: FimSlice[]
}

const COLORS = [
  "#9D7BFF", // purple
  "#3CF2FF", // cyan
  "#FF4FD8", // pink
  "#FF9F43", // orange
  "#2BFF88", // green
]

export default function FimPieChart({
  title,
  data,
}: FimPieChartProps) {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.96 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.35, ease: "easeOut" }}
      className="panel panel-glow p-6"
    >
      <div className="mb-4 text-sm tracking-wide text-text-secondary">
        {title}
      </div>

      <div className="h-64 w-full">
        <ResponsiveContainer>
          <PieChart>
            <Tooltip
              contentStyle={{
                backgroundColor: "#0E1428",
                border: "1px solid rgba(157,123,255,0.3)",
                borderRadius: "8px",
                color: "#E6E9F2",
              }}
            />

            <Pie
              data={data}
              dataKey="value"
              nameKey="name"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              isAnimationActive
            >
              {data.map((_, index) => (
                <Cell
                  key={`cell-${index}`}
                  fill={COLORS[index % COLORS.length]}
                />
              ))}
            </Pie>
          </PieChart>
        </ResponsiveContainer>
      </div>
    </motion.div>
  )
}
