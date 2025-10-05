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
    const fetchStats = async () => {
      try {
        // Get real data from search stats endpoint
        const searchStatsResponse = await fetch('http://localhost:8000/search/stats')
        if (searchStatsResponse.ok) {
          const searchData = await searchStatsResponse.json()
          setStats({
            publications: searchData.total_publications || 0,
            pages: searchData.total_pages || 0, 
            entities: searchData.total_entities || 0,
            searchIndexSize: searchData.search_index_size || 0
          })
        } else {
          // Try graph statistics as fallback
          const graphStatsResponse = await fetch('http://localhost:8000/graph/statistics')
          if (graphStatsResponse.ok) {
            const graphData = await graphStatsResponse.json()
            const nodeCounts = graphData.graph_statistics?.node_counts || []
            
            const pubCount = nodeCounts.find((n: any) => n.label?.[0] === 'Publication')?.count || 0
            const pageCount = nodeCounts.find((n: any) => n.label?.[0] === 'Page')?.count || 0  
            const entityCount = nodeCounts.find((n: any) => n.label?.[0] === 'Entity')?.count || 0
            
            setStats({
              publications: pubCount,
              pages: pageCount,
              entities: entityCount,
              searchIndexSize: 0  // No search index data from graph endpoint
            })
          } else {
            // Set to zero if no data available - NO FAKE NUMBERS
            setStats({
              publications: 0,
              pages: 0,
              entities: 0,
              searchIndexSize: 0
            })
          }
        }
      } catch (error) {
        console.error('Failed to fetch stats:', error)
        // Set to zero if error - NO FAKE NUMBERS
        setStats({
          publications: 0,
          pages: 0,
          entities: 0,
          searchIndexSize: 0
        })
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
        <div key={card.title} className="card hover:shadow-xl hover-lift transition-all duration-300 fade-in hover-glow" style={{ animationDelay: `${index * 150}ms` }}>
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-600">{card.title}</p>
              <p className="text-3xl font-bold text-gray-900 mt-1">{card.value}</p>
              <p className="text-xs text-gray-500 mt-1">{card.description}</p>
            </div>
            <div className={`w-12 h-12 ${card.color} rounded-lg flex items-center justify-center hover-zoom transition-transform duration-300`}>
              <card.icon className="w-6 h-6 text-white" />
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}