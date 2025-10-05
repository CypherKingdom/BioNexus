'use client'

import React, { useState, useEffect } from 'react'
import { NetworkIcon, SearchIcon, FilterIcon, InfoIcon, ZoomInIcon, ZoomOutIcon } from 'lucide-react'
import Link from 'next/link'
import { GraphVisualization } from '@/components/graph/GraphVisualization'

interface GraphNode {
  id: string
  label: string
  type: string
  properties: Record<string, any>
}

interface GraphEdge {
  source: string
  target: string
  type: string
  properties: Record<string, any>
}

interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

export default function KnowledgeGraphPage() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    fetchGraphData()
  }, [])

  const fetchGraphData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/kg/explore?limit=50')
      if (response.ok) {
        const data = await response.json()
        setGraphData({
          nodes: data.nodes || [],
          edges: data.relationships || []
        })
      } else {
        setError('Knowledge graph service unavailable')
        setGraphData({ nodes: [], edges: [] })
      }
    } catch (err) {
      console.error('Failed to fetch graph data:', err)
      setError('Unable to load knowledge graph - backend unavailable')
      setGraphData({ nodes: [], edges: [] })
    } finally {
      setLoading(false)
    }
  }

  const searchGraph = async () => {
    if (!searchQuery.trim()) {
      fetchGraphData()
      return
    }

    setLoading(true)
    try {
      const response = await fetch(`http://localhost:8000/kg/search?query=${encodeURIComponent(searchQuery)}&limit=30`)
      if (response.ok) {
        const data = await response.json()
        setGraphData({
          nodes: data.nodes || [],
          edges: data.relationships || []
        })
      } else {
        setError('Graph search failed')
      }
    } catch (err) {
      console.error('Graph search failed:', err)
      setError('Search unavailable')
    } finally {
      setLoading(false)
    }
  }

  const getNodeColor = (nodeType: string) => {
    const colors = {
      'Publication': 'bg-blue-500',
      'Entity': 'bg-green-500',
      'Page': 'bg-purple-500',
      'Author': 'bg-orange-500',
      'Organism': 'bg-emerald-500',
      'Gene': 'bg-red-500',
      'Protein': 'bg-indigo-500',
      default: 'bg-gray-500'
    }
    return colors[nodeType as keyof typeof colors] || colors.default
  }

  const getNodeTypeIcon = (nodeType: string) => {
    // Return appropriate icon based on node type
    return <div className="w-2 h-2 rounded-full bg-white"></div>
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <NetworkIcon className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Knowledge Graph</h1>
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link href="/" className="text-gray-600 hover:text-primary-700 transition-colors">Home</Link>
              <Link href="/search" className="text-gray-600 hover:text-primary-700 transition-colors">Search</Link>
              <Link href="/export" className="text-gray-600 hover:text-primary-700 transition-colors">Export</Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Controls */}
        <div className="mb-8">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 text-center mb-6">
              Explore Research Connections
            </h2>
            <p className="text-gray-600 text-center mb-8">
              Visualize relationships between publications, entities, and research concepts
            </p>
            
            <div className="flex gap-4 mb-6">
              <div className="flex-1 relative">
                <SearchIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyDown={(e) => e.key === 'Enter' && searchGraph()}
                  placeholder="Search for entities, publications, or concepts..."
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none"
                />
              </div>
              <button
                onClick={searchGraph}
                className="px-6 py-3 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors"
              >
                Search Graph
              </button>
            </div>

            {/* Graph Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-primary-600">{graphData.nodes.length}</div>
                <div className="text-sm text-gray-600">Nodes</div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-primary-600">{graphData.edges.length}</div>
                <div className="text-sm text-gray-600">Relationships</div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {new Set(graphData.nodes.map(n => n.type)).size}
                </div>
                <div className="text-sm text-gray-600">Node Types</div>
              </div>
              <div className="bg-white rounded-lg p-4 text-center">
                <div className="text-2xl font-bold text-primary-600">
                  {new Set(graphData.edges.map(e => e.type)).size}
                </div>
                <div className="text-sm text-gray-600">Edge Types</div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Graph Area */}
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Graph Visualization */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              {loading ? (
                <div className="h-96 flex items-center justify-center">
                  <div className="text-center">
                    <div className="w-8 h-8 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-gray-600">Loading knowledge graph...</p>
                  </div>
                </div>
              ) : error ? (
                <div className="h-96 flex items-center justify-center">
                  <div className="text-center">
                    <NetworkIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">Graph Unavailable</h3>
                    <p className="text-gray-600 mb-4">{error}</p>
                    <button
                      onClick={fetchGraphData}
                      className="btn-outline"
                    >
                      Retry Connection
                    </button>
                  </div>
                </div>
              ) : graphData.nodes.length === 0 ? (
                <div className="h-96 flex items-center justify-center">
                  <div className="text-center">
                    <NetworkIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                    <h3 className="text-lg font-medium text-gray-900 mb-2">No Graph Data</h3>
                    <p className="text-gray-600">No nodes found in the knowledge graph</p>
                  </div>
                </div>
              ) : (
                <div className="h-96 relative">
                  <GraphVisualization
                    nodes={graphData.nodes}
                    edges={graphData.edges}
                    width={800}
                    height={384}
                    onNodeClick={setSelectedNode}
                  />
                  
                  {/* Graph controls */}
                  <div className="absolute top-4 right-4 flex flex-col gap-2">
                    <button className="p-2 bg-white rounded-lg shadow border border-gray-200 hover:bg-gray-50">
                      <ZoomInIcon className="w-4 h-4" />
                    </button>
                    <button className="p-2 bg-white rounded-lg shadow border border-gray-200 hover:bg-gray-50">
                      <ZoomOutIcon className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Node Types Legend */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Node Types</h3>
              <div className="space-y-2">
                {Array.from(new Set(graphData.nodes.map(n => n.type))).map(type => (
                  <div key={type} className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${getNodeColor(type)}`}></div>
                    <span className="text-sm text-gray-700">{type}</span>
                    <span className="text-xs text-gray-500 ml-auto">
                      {graphData.nodes.filter(n => n.type === type).length}
                    </span>
                  </div>
                ))}
              </div>
            </div>

            {/* Selected Node Details */}
            {selectedNode && (
              <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
                <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <InfoIcon className="w-4 h-4" />
                  Node Details
                </h3>
                <div className="space-y-3">
                  <div>
                    <label className="text-sm font-medium text-gray-600">Type</label>
                    <p className="text-sm text-gray-900">{selectedNode.type}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">Label</label>
                    <p className="text-sm text-gray-900">{selectedNode.label}</p>
                  </div>
                  <div>
                    <label className="text-sm font-medium text-gray-600">ID</label>
                    <p className="text-sm text-gray-900 font-mono">{selectedNode.id}</p>
                  </div>
                  {Object.keys(selectedNode.properties).length > 0 && (
                    <div>
                      <label className="text-sm font-medium text-gray-600">Properties</label>
                      <div className="text-xs text-gray-700 mt-1 space-y-1">
                        {Object.entries(selectedNode.properties).map(([key, value]) => (
                          <div key={key} className="flex justify-between">
                            <span className="font-medium">{key}:</span>
                            <span className="text-right">{String(value)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            )}

            {/* Graph Actions */}
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h3 className="font-semibold text-gray-900 mb-4">Actions</h3>
              <div className="space-y-2">
                <button
                  onClick={fetchGraphData}
                  className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors"
                >
                  Refresh Graph
                </button>
                <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                  Export View
                </button>
                <button className="w-full text-left px-3 py-2 text-sm text-gray-700 hover:bg-gray-50 rounded-lg transition-colors">
                  Center Graph
                </button>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}