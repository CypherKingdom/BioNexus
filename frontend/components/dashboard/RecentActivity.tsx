'use client'

import { useState, useEffect } from 'react'
import { ExternalLinkIcon, ClockIcon } from 'lucide-react'
import Link from 'next/link'

interface ActivityItem {
  id: string
  title: string
  type: 'publication' | 'search' | 'discovery'
  description: string
  timestamp: string
  url?: string
}

export function RecentActivity() {
  const [activities, setActivities] = useState<ActivityItem[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    // Fetch real recent publications from Neo4j
    const fetchActivity = async () => {
      try {
        // Get recent publications from search endpoint
        const response = await fetch('http://localhost:8000/search/semantic?query=recent&top_k=5')
        if (response.ok) {
          const data = await response.json()
          const recentActivities: ActivityItem[] = data.results.slice(0, 5).map((result: any, index: number) => ({
            id: result.id || `activity_${index}`,
            title: result.title || 'Unknown Publication',
            type: 'publication' as const,
            description: `Publication with ${result.entities?.length || 0} entities: ${result.entities?.slice(0, 2).join(', ') || 'No entities'}`,
            timestamp: result.year ? `Year ${result.year}` : 'Unknown date',
            url: `/search?q=${encodeURIComponent(result.title || '')}`
          }))
          
          setActivities(recentActivities.length > 0 ? recentActivities : [])
        } else {
          // No data available - show empty state
          setActivities([])
        }
      } catch (error) {
        console.error('Failed to fetch recent activity:', error)
        // No fake data - show empty state
        setActivities([])
      } finally {
        setLoading(false)
      }
    }

    fetchActivity()
  }, [])

  const getActivityIcon = (type: ActivityItem['type']) => {
    const iconClasses = "w-4 h-4"
    
    switch (type) {
      case 'publication':
        return <div className="w-2 h-2 bg-green-500 rounded-full"></div>
      case 'search':
        return <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
      case 'discovery':
        return <div className="w-2 h-2 bg-purple-500 rounded-full"></div>
      default:
        return <div className="w-2 h-2 bg-gray-500 rounded-full"></div>
    }
  }

  const getActivityBadge = (type: ActivityItem['type']) => {
    switch (type) {
      case 'publication':
        return <span className="entity-badge bg-green-100 text-green-800">Publication</span>
      case 'search':
        return <span className="entity-badge bg-blue-100 text-blue-800">Search</span>
      case 'discovery':
        return <span className="entity-badge bg-purple-100 text-purple-800">Discovery</span>
      default:
        return null
    }
  }

  if (loading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="flex items-start space-x-3 animate-pulse">
            <div className="w-2 h-2 bg-gray-300 rounded-full mt-2"></div>
            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <div className="h-4 bg-gray-200 rounded w-48"></div>
                <div className="h-4 bg-gray-200 rounded w-16"></div>
              </div>
              <div className="h-3 bg-gray-200 rounded w-full mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-20"></div>
            </div>
          </div>
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {activities.map((activity) => (
        <div key={activity.id} className="flex items-start space-x-3 group">
          <div className="mt-2">
            {getActivityIcon(activity.type)}
          </div>
          
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-2 mb-1">
              <h4 className="text-sm font-medium text-gray-900 truncate">
                {activity.title}
              </h4>
              {getActivityBadge(activity.type)}
              {activity.url && (
                <Link 
                  href={activity.url}
                  className="opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <ExternalLinkIcon className="w-3 h-3 text-gray-400 hover:text-primary-500" />
                </Link>
              )}
            </div>
            
            <p className="text-xs text-gray-600 mb-2 line-clamp-2">
              {activity.description}
            </p>
            
            <div className="flex items-center space-x-1 text-xs text-gray-500">
              <ClockIcon className="w-3 h-3" />
              <span>{activity.timestamp}</span>
            </div>
          </div>
        </div>
      ))}
      
      <div className="pt-4 border-t border-gray-200">
        <Link 
          href="/activity" 
          className="text-sm text-primary-600 hover:text-primary-700 font-medium"
        >
          View all activity →
        </Link>
      </div>
    </div>
  )
}