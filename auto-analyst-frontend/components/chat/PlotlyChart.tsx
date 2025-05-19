"use client"

import dynamic from "next/dynamic"
import React, { useRef, useEffect, useState } from "react"

// Dynamically import Plot to avoid SSR issues
const Plot = dynamic(() => import("react-plotly.js"), { ssr: false })

interface PlotlyChartProps {
  data: any[]
  layout?: any
}

const PlotlyChart: React.FC<PlotlyChartProps> = ({ data, layout = {} }) => {
  const containerRef = useRef<HTMLDivElement>(null)
  const [dimensions, setDimensions] = useState({ width: 0, height: 0 })
  const [error, setError] = useState<string | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  // Validate the data for proper Plotly format
  const safeData = React.useMemo(() => {
    try {
      if (!Array.isArray(data)) {
        console.error("PlotlyChart: data is not an array", data)
        setError("Invalid chart data format")
        return []
      }
      
      // Make a copy to avoid modifying props
      return data.map(trace => {
        // Ensure trace has required properties
        if (!trace.type) {
          return { ...trace, type: 'scatter' }
        }
        return trace
      })
    } catch (err) {
      console.error("PlotlyChart: Error processing data", err)
      setError("Error processing chart data")
      return []
    }
  }, [data])

  // Safe layout with defaults
  const safeLayout = React.useMemo(() => {
    try {
      return {
        autosize: true,
        margin: { l: 50, r: 50, b: 50, t: 50, pad: 4 },
        ...layout
      }
    } catch (err) {
      console.error("PlotlyChart: Error processing layout", err)
      return { autosize: true }
    }
  }, [layout])

  useEffect(() => {
    if (containerRef.current) {
      const { width } = containerRef.current.getBoundingClientRect()
      setDimensions({ width, height: Math.max(300, width * 0.6) })
    }
    
    // Set loading to false after a short delay
    const timer = setTimeout(() => {
      setIsLoading(false)
    }, 500)
    
    return () => clearTimeout(timer)
  }, [])

  // Handle window resize
  useEffect(() => {
    const handleResize = () => {
      if (containerRef.current) {
        const { width } = containerRef.current.getBoundingClientRect()
        setDimensions({ width, height: Math.max(300, width * 0.6) })
      }
    }

    window.addEventListener("resize", handleResize)
    return () => window.removeEventListener("resize", handleResize)
  }, [])

  if (error) {
    return (
      <div className="p-4 border border-red-200 rounded bg-red-50 text-red-800">
        <p className="font-medium">Chart Error</p>
        <p className="text-sm">{error}</p>
        <p className="text-xs mt-2">Please try refreshing or contact support if the issue persists.</p>
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-60 bg-gray-50 rounded">
        <div className="animate-pulse text-gray-500">Loading chart...</div>
      </div>
    )
  }

  if (safeData.length === 0) {
    return (
      <div className="p-4 border border-gray-200 rounded bg-gray-50">
        <p className="text-center text-gray-500">No chart data available</p>
      </div>
    )
  }

  return (
    <div ref={containerRef} className="w-full overflow-hidden">
      <Plot
        data={safeData}
        layout={{
          ...safeLayout,
          width: dimensions.width,
          height: dimensions.height,
        }}
        config={{
          responsive: true,
          displayModeBar: true,
          displaylogo: false,
          modeBarButtonsToRemove: [
            'sendDataToCloud',
            'lasso2d',
            'autoScale2d',
          ],
        }}
        style={{ width: "100%", height: "100%" }}
        onError={(err) => {
          console.error("Plotly rendering error:", err)
          setError("Failed to render chart")
        }}
      />
    </div>
  )
}

export default PlotlyChart
