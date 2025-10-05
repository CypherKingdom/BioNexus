'use client'

import { useState, useEffect } from 'react'
import { SimpleBarChart } from '@/components/charts/SimpleCharts'

interface TopicData {
  topic: string
  publications: number
  growth: number
  trend: 'up' | 'down' | 'stable'
}

export function TopicTrends() {
  const [topics, setTopics] = useState<TopicData[]>([])
  const [loading, setLoading] = useState(true)
  const [viewMode, setViewMode] = useState<'chart' | 'list'>('chart')

  useEffect(() => {
    // Simulate fetching topic trends
    const fetchTopics = async () => {
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const mockTopics: TopicData[] = [
        { topic: 'Microgravity Effects', publications: 156, growth: 12.5, trend: 'up' },
        { topic: 'Radiation Exposure', publications: 142, growth: 8.2, trend: 'up' },
        { topic: 'Cardiovascular Adaptation', publications: 98, growth: -2.1, trend: 'down' },
        { topic: 'Bone Density', publications: 87, growth: 15.3, trend: 'up' },
        { topic: 'Plant Growth', publications: 72, growth: 5.7, trend: 'up' },
        { topic: 'Neural Function', publications: 64, growth: 0.8, trend: 'stable' },
        { topic: 'Sleep Patterns', publications: 45, growth: 22.1, trend: 'up' },
        { topic: 'Muscle Atrophy', publications: 38, growth: -5.3, trend: 'down' }
      ]
      
      setTopics(mockTopics)
      setLoading(false)
    }

    fetchTopics()
  }, [])

  const getTrendColor = (trend: TopicData['trend']) => {
    switch (trend) {
      case 'up': return 'text-green-600'
      case 'down': return 'text-red-600'
      case 'stable': return 'text-gray-600'
      default: return 'text-gray-600'
    }
  }

  const getTrendIcon = (trend: TopicData['trend']) => {
    switch (trend) {
      case 'up': return '↗'
      case 'down': return '↘'
      case 'stable': return '→'
      default: return '→'
    }
  }

  const plotData = [{
    x: topics.map(t => t.topic),
    y: topics.map(t => t.publications),
    type: 'bar' as const,
    marker: {
      color: topics.map(t => {
        switch (t.trend) {
          case 'up': return '#10b981'
          case 'down': return '#ef4444'
          case 'stable': return '#6b7280'
          default: return '#6b7280'
        }
      })
    }
  }]

  const plotLayout = {
    title: '',
    xaxis: { 
      title: '',
      tickangle: -45,
      tickfont: { size: 10 }
    },
    yaxis: { title: 'Publications' },
    margin: { l: 40, r: 20, t: 20, b: 80 },
    height: 300,
    plot_bgcolor: 'transparent',
    paper_bgcolor: 'transparent'
  }

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="flex justify-between items-center mb-4">
          <div className="h-4 bg-gray-200 rounded w-32"></div>
          <div className="h-8 bg-gray-200 rounded w-20"></div>
        </div>
        <div className="h-64 bg-gray-200 rounded"></div>
      </div>
    )
  }

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <h4 className="text-sm font-medium text-gray-600">Research Focus Areas</h4>
        <div className="flex bg-gray-100 rounded-lg p-1">
          <button
            onClick={() => setViewMode('chart')}
            className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
              viewMode === 'chart'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            Chart
          </button>
          <button
            onClick={() => setViewMode('list')}
            className={`px-3 py-1 text-xs font-medium rounded transition-colors ${
              viewMode === 'list'
                ? 'bg-white text-gray-900 shadow-sm'
                : 'text-gray-600 hover:text-gray-900'
            }`}
          >
            List
          </button>
        </div>
      </div>

      {viewMode === 'chart' ? (
        <SimpleBarChart
          data={topics.slice(0, 6).map(topic => ({
            label: topic.topic.split(' ')[0],
            value: topic.publications,
            color: topic.trend === 'up' ? '#10b981' : topic.trend === 'down' ? '#ef4444' : '#6b7280'
          }))}
          title=""
          height={240}
        />
      ) : (
        <div className="space-y-3 max-h-64 overflow-y-auto scrollbar-thin">
          {topics.map((topic, index) => (
            <div key={topic.topic} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center space-x-3">
                <span className="text-sm font-medium text-gray-900 w-4">
                  {index + 1}
                </span>
                <div>
                  <p className="text-sm font-medium text-gray-900">{topic.topic}</p>
                  <p className="text-xs text-gray-600">{topic.publications} publications</p>
                </div>
              </div>
              
              <div className={`flex items-center space-x-1 text-xs font-medium ${getTrendColor(topic.trend)}`}>
                <span>{getTrendIcon(topic.trend)}</span>
                <span>{Math.abs(topic.growth)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}