'use client'

import React from 'react'

interface ChartData {
  label: string
  value: number
  color: string
}

interface SimpleBarChartProps {
  data: ChartData[]
  title: string
  height?: number
}

export function SimpleBarChart({ data, title, height = 200 }: SimpleBarChartProps) {
  const maxValue = Math.max(...data.map(d => d.value))
  
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="space-y-3" style={{ height: `${height}px` }}>
        {data.map((item, index) => (
          <div key={index} className="flex items-center gap-3">
            <div className="w-20 text-sm text-gray-600 text-right">
              {item.label}
            </div>
            <div className="flex-1 relative">
              <div
                className="h-6 rounded-md transition-all duration-500"
                style={{
                  backgroundColor: item.color,
                  width: `${(item.value / maxValue) * 100}%`,
                  minWidth: '20px'
                }}
              />
              <div className="absolute right-2 top-0 h-6 flex items-center">
                <span className="text-xs font-medium text-white">
                  {item.value}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

interface SimpleLineChartProps {
  data: { month: string; value: number }[]
  title: string
  height?: number
}

export function SimpleLineChart({ data, title, height = 200 }: SimpleLineChartProps) {
  if (data.length === 0) return null
  
  const maxValue = Math.max(...data.map(d => d.value))
  const minValue = Math.min(...data.map(d => d.value))
  const range = maxValue - minValue || 1
  
  const points = data.map((item, index) => {
    const x = (index / (data.length - 1)) * 100
    const y = 100 - ((item.value - minValue) / range) * 100
    return `${x},${y}`
  }).join(' ')
  
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="relative" style={{ height: `${height}px` }}>
        <svg 
          width="100%" 
          height="100%" 
          viewBox="0 0 100 100" 
          className="border border-gray-200 rounded-lg bg-gray-50"
        >
          {/* Grid lines */}
          {[0, 25, 50, 75, 100].map(y => (
            <line
              key={y}
              x1="0"
              y1={y}
              x2="100"
              y2={y}
              stroke="#e5e7eb"
              strokeWidth="0.5"
            />
          ))}
          
          {/* Data line */}
          <polyline
            points={points}
            fill="none"
            stroke="#3b82f6"
            strokeWidth="2"
            className="drop-shadow-sm"
          />
          
          {/* Data points */}
          {data.map((item, index) => {
            const x = (index / (data.length - 1)) * 100
            const y = 100 - ((item.value - minValue) / range) * 100
            return (
              <g key={index}>
                <circle
                  cx={x}
                  cy={y}
                  r="2"
                  fill="#3b82f6"
                  stroke="white"
                  strokeWidth="1"
                />
                <text
                  x={x}
                  y="95"
                  textAnchor="middle"
                  fontSize="3"
                  fill="#6b7280"
                >
                  {item.month}
                </text>
              </g>
            )
          })}
        </svg>
        
        {/* Y-axis labels */}
        <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-500 -ml-8">
          <span>{maxValue}</span>
          <span>{Math.round((maxValue + minValue) / 2)}</span>
          <span>{minValue}</span>
        </div>
      </div>
    </div>
  )
}

interface PieChartProps {
  data: ChartData[]
  title: string
  size?: number
}

export function SimplePieChart({ data, title, size = 150 }: PieChartProps) {
  const total = data.reduce((sum, item) => sum + item.value, 0)
  let currentAngle = 0
  
  const slices = data.map(item => {
    const percentage = (item.value / total) * 100
    const angle = (item.value / total) * 360
    const startAngle = currentAngle
    const endAngle = currentAngle + angle
    currentAngle += angle
    
    const largeArcFlag = angle > 180 ? 1 : 0
    const x1 = 50 + 40 * Math.cos((startAngle * Math.PI) / 180)
    const y1 = 50 + 40 * Math.sin((startAngle * Math.PI) / 180)
    const x2 = 50 + 40 * Math.cos((endAngle * Math.PI) / 180)
    const y2 = 50 + 40 * Math.sin((endAngle * Math.PI) / 180)
    
    const pathData = `M 50 50 L ${x1} ${y1} A 40 40 0 ${largeArcFlag} 1 ${x2} ${y2} Z`
    
    return {
      ...item,
      pathData,
      percentage: percentage.toFixed(1)
    }
  })
  
  return (
    <div className="p-4">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      <div className="flex items-center gap-6">
        <svg width={size} height={size} viewBox="0 0 100 100">
          {slices.map((slice, index) => (
            <path
              key={index}
              d={slice.pathData}
              fill={slice.color}
              stroke="white"
              strokeWidth="1"
              className="hover:opacity-80 transition-opacity"
            />
          ))}
        </svg>
        
        <div className="space-y-2">
          {slices.map((slice, index) => (
            <div key={index} className="flex items-center gap-2 text-sm">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: slice.color }}
              />
              <span className="text-gray-700">{slice.label}</span>
              <span className="text-gray-500">({slice.percentage}%)</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}