'use client'

import { useEffect, useState } from 'react'
import { TrendingUpIcon, UsersIcon, FileTextIcon, NetworkIcon } from 'lucide-react'

interface Stats {
  publications: number
  pages: number
  entities: number
  searchIndexSize: number
}

export function StatsCards() {
  const [stats, setStats] = useState<Stats>({
    publications: 0,
    pages: 0,
    entities: 0,
    searchIndexSize: 0
  })
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Simulate API call - in real app, fetch from backend
    const fetchStats = async () => {
      try {
        // Mock data - replace with actual API call
        await new Promise(resolve => setTimeout(resolve, 1000))
        setStats({
          publications: 608,
          pages: 15420,
          entities: 8934,
          searchIndexSize: 15420
        })
      } catch (error) {
        console.error('Failed to fetch stats:', error)
      } finally {
        setLoading(false)
      }
    }

    fetchStats()
  }, [])

  const statCards = [
    {
      title: 'Publications',
      value: stats.publications,
      icon: FileTextIcon,
      color: 'bg-primary-500',
      description: 'NASA bioscience publications'
    },
    {
      title: 'Total Pages',
      value: stats.pages.toLocaleString(),
      icon: FileTextIcon,
      color: 'bg-blue-500',
      description: 'Pages processed with OCR'
    },
    {
      title: 'Entities Extracted',
      value: stats.entities.toLocaleString(),
      icon: NetworkIcon,
      color: 'bg-green-500',
      description: 'Organisms, endpoints, instruments'
    },
    {
      title: 'Search Index',
      value: stats.searchIndexSize.toLocaleString(),
      icon: TrendingUpIcon,
      color: 'bg-purple-500',
      description: 'Pages with embeddings'
    }
  ]

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="card animate-pulse">
            <div className="flex items-center justify-between">
              <div>
                <div className="h-4 bg-gray-200 rounded w-20 mb-2"></div>
                <div className="h-8 bg-gray-200 rounded w-16 mb-1"></div>
                <div className="h-3 bg-gray-200 rounded w-24"></div>
              </div>
              <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statCards.map((card, index) => (
        <div key={card.title} className="card hover:shadow-lg transition-all duration-200 animate-fade-in" style={{ animationDelay: `${index * 100}ms` }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{card.title}</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{card.value}</p>
              <p className="text-xs text-gray-500 mt-1">{card.description}</p>
            </div>
            <div className={`w-12 h-12 ${card.color} rounded-lg flex items-center justify-center`}>
              <card.icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}