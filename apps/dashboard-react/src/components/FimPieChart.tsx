import { motion } from "framer-motion"
import dynamic from "next/dynamic"
import type { EChartsOption } from "echarts"
import { useMemo } from "react"

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false })

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
  const option = useMemo<EChartsOption>(
    () => ({
      animationDuration: 880,
      animationEasing: "cubicOut",
      tooltip: {
        trigger: "item",
        backgroundColor: "#102635",
        borderColor: "rgba(66,229,255,0.28)",
        borderWidth: 1,
        textStyle: { color: "#E8F7FF" },
      },
      legend: {
        show: true,
        bottom: 0,
        itemWidth: 10,
        itemHeight: 10,
        textStyle: {
          color: "#9EC7D9",
          fontSize: 11,
        },
      },
      series: [
        {
          name: "Signal Mix",
          type: "pie",
          radius: ["42%", "74%"],
          center: ["50%", "44%"],
          avoidLabelOverlap: true,
          padAngle: 2,
          itemStyle: {
            borderColor: "#061017",
            borderWidth: 2,
          },
          label: {
            color: "#E8F7FF",
            formatter: "{b|{b}}\n{c} ({d}%)",
            rich: {
              b: {
                color: "#9EC7D9",
                fontSize: 10,
                fontWeight: 500,
              },
            },
          },
          data: data.map((item, index) => ({
            value: item.value,
            name: item.name,
            itemStyle: {
              color: COLORS[index % COLORS.length],
              shadowBlur: 18,
              shadowColor: `${COLORS[index % COLORS.length]}55`,
            },
          })),
        },
      ],
    }),
    [data]
  )

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
          <ReactECharts
            option={option}
            style={{ width: "100%", height: "100%" }}
            notMerge
            lazyUpdate
          />
        )}
      </div>
    </motion.section>
  )
}
