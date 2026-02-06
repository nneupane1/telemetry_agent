import { motion } from "framer-motion"
import dynamic from "next/dynamic"
import type { EChartsOption } from "echarts"
import { useMemo } from "react"

const ReactECharts = dynamic(() => import("echarts-for-react"), { ssr: false })

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
  const option = useMemo<EChartsOption>(() => {
    const anomalies = data
      .filter((point) => point.isAnomaly)
      .map((point) => [point.timestamp, point.value])

    return {
      animationDuration: 850,
      animationEasing: "cubicOut",
      tooltip: {
        trigger: "axis",
        axisPointer: {
          type: "line",
          lineStyle: { color: "rgba(66,229,255,0.45)" },
        },
        backgroundColor: "#102635",
        borderColor: "rgba(66,229,255,0.28)",
        borderWidth: 1,
        textStyle: {
          color: "#E8F7FF",
        },
      },
      grid: {
        left: 42,
        right: 18,
        top: 26,
        bottom: 30,
      },
      xAxis: {
        type: "category",
        boundaryGap: false,
        data: data.map((point) => point.timestamp),
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: {
          color: "#9EC7D9",
          fontSize: 11,
        },
      },
      yAxis: {
        type: "value",
        splitNumber: 4,
        axisLine: { show: false },
        axisTick: { show: false },
        axisLabel: { color: "#9EC7D9", fontSize: 11 },
        splitLine: {
          lineStyle: {
            color: "rgba(255,255,255,0.08)",
            type: "dashed",
          },
        },
      },
      series: [
        {
          name: "Stability",
          type: "line",
          smooth: true,
          showSymbol: false,
          lineStyle: {
            width: 3,
            color,
            shadowBlur: 14,
            shadowColor: "rgba(66,229,255,0.32)",
          },
          areaStyle: {
            color: "rgba(66,229,255,0.1)",
          },
          data: data.map((point) => point.value),
        },
        {
          name: "Anomaly",
          type: "scatter",
          symbolSize: 9,
          data: anomalies,
          itemStyle: {
            color: "#FF8C42",
            borderColor: "#FFC188",
            borderWidth: 1,
            shadowBlur: 14,
            shadowColor: "rgba(255,140,66,0.35)",
          },
        },
      ],
    }
  }, [color, data])

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
