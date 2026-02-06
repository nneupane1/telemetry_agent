import { motion } from "framer-motion"
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip } from "recharts"

interface FimSlice {
  name: string
  value: number
}

interface FimPieChartProps {
  title: string
  data: FimSlice[]
}

const COLORS = ["#42E5FF", "#FF8C42", "#7CF7A5", "#53C8D8", "#FFB347"]

export default function FimPieChart({ title, data }: FimPieChartProps) {
  return (
    <motion.section
      initial={{ opacity: 0, scale: 0.97 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.28, ease: "easeOut" }}
      className="panel panel-glow p-5"
    >
      <div className="text-kicker">Failure Driver Mix</div>
      <h3 className="text-base">{title}</h3>
      <div className="h-64 mt-3">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-sm text-text-muted border border-dashed border-neon-cyan/20 rounded-lg">
            No distribution values available.
          </div>
        ) : (
          <ResponsiveContainer>
            <PieChart>
              <Tooltip
                contentStyle={{
                  backgroundColor: "#102635",
                  border: "1px solid rgba(66,229,255,0.28)",
                  borderRadius: "10px",
                  color: "#E8F7FF",
                }}
              />
              <Pie
                data={data}
                dataKey="value"
                nameKey="name"
                innerRadius={58}
                outerRadius={92}
                paddingAngle={2}
                isAnimationActive
              >
                {data.map((_, index) => (
                  <Cell key={`slice-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
            </PieChart>
          </ResponsiveContainer>
        )}
      </div>
    </motion.section>
  )
}

