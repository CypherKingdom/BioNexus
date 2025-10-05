'use client'

import React, { useState, useEffect, useCallback } from 'react'
import { 
  NetworkIcon, SearchIcon, InfoIcon, BarChart3Icon, RefreshCwIcon, 
  FilterIcon, LayoutGridIcon, ZoomInIcon, ZoomOutIcon, SettingsIcon,
  ChevronDownIcon, ChevronUpIcon, ChevronRightIcon, EyeIcon, EyeOffIcon, PlayIcon,
  PauseIcon, RotateCcwIcon, DownloadIcon, MaximizeIcon
} from 'lucide-react'
import { GraphVisualization } from '@/components/graph/GraphVisualization'
import { SearchBar } from '@/components/search/SearchBar'
import { ErrorBoundary, safeRender, validateForReact } from '@/components/ErrorBoundary'

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
  metadata?: {
    total_nodes: number
    total_edges: number
    query_time_ms: number
  }
}

interface FilterOptions {
  nodeTypes: string[]
  relationshipTypes: string[]
  minConnections: number
  maxNodes: number
  showLabels: boolean
  nodeSize: number
  edgeWidth: number
  layout: 'force' | 'circular' | 'grid' | 'hierarchical'
  physics: boolean
}

interface GraphStats {
  totalNodes: number
  totalEdges: number
  nodeTypes: { [key: string]: number }
  relationshipTypes: { [key: string]: number }
  avgConnections: number
  maxConnections: number
}

export default function KnowledgeGraphPage() {
  const [graphData, setGraphData] = useState<GraphData>({ nodes: [], edges: [] })
  const [filteredData, setFilteredData] = useState<GraphData>({ nodes: [], edges: [] })
  const [searchQuery, setSearchQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null)
  const [stats, setStats] = useState<GraphStats | null>(null)
  const [showFilters, setShowFilters] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const [availableNodeTypes, setAvailableNodeTypes] = useState<string[]>([])
  const [availableRelTypes, setAvailableRelTypes] = useState<string[]>([])
  
  const [filters, setFilters] = useState<FilterOptions>({
    nodeTypes: [],
    relationshipTypes: [],
    minConnections: 0,
    maxNodes: 200,
    showLabels: true,
    nodeSize: 15,
    edgeWidth: 1,
    layout: 'force',
    physics: true
  })

  // Apply filters to graph data
  const applyFilters = useCallback((data: GraphData) => {
    let filteredNodes = data.nodes
    let filteredEdges = data.edges

    // Filter by node types
    if (filters.nodeTypes.length > 0) {
      filteredNodes = filteredNodes.filter(node => filters.nodeTypes.includes(node.type))
    }

    // Filter by minimum connections
    if (filters.minConnections > 0) {
      const nodeConnections = new Map<string, number>()
      filteredEdges.forEach(edge => {
        nodeConnections.set(edge.source, (nodeConnections.get(edge.source) || 0) + 1)
        nodeConnections.set(edge.target, (nodeConnections.get(edge.target) || 0) + 1)
      })
      filteredNodes = filteredNodes.filter(node => 
        (nodeConnections.get(node.id) || 0) >= filters.minConnections
      )
    }

    // Limit number of nodes
    if (filteredNodes.length > filters.maxNodes) {
      filteredNodes = filteredNodes.slice(0, filters.maxNodes)
    }

    // Filter edges to only include those between remaining nodes
    const nodeIds = new Set(filteredNodes.map(n => n.id))
    filteredEdges = filteredEdges.filter(edge => 
      nodeIds.has(edge.source) && nodeIds.has(edge.target)
    )

    // Filter by relationship types
    if (filters.relationshipTypes.length > 0) {
      filteredEdges = filteredEdges.filter(edge => 
        filters.relationshipTypes.includes(edge.type)
      )
    }

    return { nodes: filteredNodes, edges: filteredEdges }
  }, [filters])

  // Calculate graph statistics
  const calculateStats = useCallback((data: GraphData): GraphStats => {
    const nodeTypes: { [key: string]: number } = {}
    const relationshipTypes: { [key: string]: number } = {}
    const nodeConnections = new Map<string, number>()

    data.nodes.forEach(node => {
      nodeTypes[node.type] = (nodeTypes[node.type] || 0) + 1
    })

    data.edges.forEach(edge => {
      relationshipTypes[edge.type] = (relationshipTypes[edge.type] || 0) + 1
      nodeConnections.set(edge.source, (nodeConnections.get(edge.source) || 0) + 1)
      nodeConnections.set(edge.target, (nodeConnections.get(edge.target) || 0) + 1)
    })

    const connections = Array.from(nodeConnections.values())
    const avgConnections = connections.length > 0 ? connections.reduce((a, b) => a + b, 0) / connections.length : 0
    const maxConnections = connections.length > 0 ? Math.max(...connections) : 0

    return {
      totalNodes: data.nodes.length,
      totalEdges: data.edges.length,
      nodeTypes,
      relationshipTypes,
      avgConnections: Math.round(avgConnections * 10) / 10,
      maxConnections
    }
  }, [])

  // Load initial graph data
  const loadGraphData = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/graph/explore?limit=100')
      if (response.ok) {
        const data = await response.json()
        
        // Validate the data structure before processing
        try {
          validateForReact(data, 'graphResponse')
        } catch (error) {
          console.error('Graph response validation failed:', error)
          setError('Invalid data structure received from server')
          return
        }
        
        // Clean all incoming node data
        const cleanNodes: GraphNode[] = (data.nodes || []).map((node: any) => {
          const cleanProperties: Record<string, string> = {}
          
          if (node.properties && typeof node.properties === 'object') {
            Object.entries(node.properties).forEach(([key, value]) => {
              try {
                if (value === null || value === undefined) {
                  cleanProperties[key] = 'N/A'
                } else if (typeof value === 'string') {
                  cleanProperties[key] = value
                } else if (typeof value === 'number' || typeof value === 'boolean') {
                  cleanProperties[key] = String(value)
                } else if (Array.isArray(value)) {
                  cleanProperties[key] = value.map(v => String(v || 'N/A')).join(', ')
                } else if (typeof value === 'object') {
                  cleanProperties[key] = JSON.stringify(value)
                } else {
                  cleanProperties[key] = String(value)
                }
              } catch (e) {
                cleanProperties[key] = 'Invalid data'
              }
            })
          }
          
          return {
            id: String(node.id || ''),
            label: String(node.label || 'Unknown'),
            type: String(node.type || 'Unknown'),
            properties: cleanProperties
          }
        })
        
        // Clean edge data
        const cleanEdges: GraphEdge[] = (data.edges || []).map((edge: any) => ({
          source: String(edge.source || ''),
          target: String(edge.target || ''),
          type: String(edge.type || 'RELATED'),
          properties: {} // Keep edge properties simple for now
        }))
        
        const newGraphData = {
          nodes: cleanNodes,
          edges: cleanEdges,
          metadata: data.metadata
        }
        
        setGraphData(newGraphData)
        
        // Update available types for filtering
        const nodeTypes = Array.from(new Set(cleanNodes.map(n => n.type)))
        const relTypes = Array.from(new Set(cleanEdges.map(e => e.type)))
        setAvailableNodeTypes(nodeTypes)
        setAvailableRelTypes(relTypes)
        
        // Calculate and set statistics
        const graphStats = calculateStats(newGraphData)
        setStats(graphStats)
      } else {
        setError('Failed to load graph data')
      }
    } catch (err) {
      console.error('Graph data loading failed:', err)
      setError('Unable to connect to backend server')
    } finally {
      setLoading(false)
    }
  }

  // Search within the graph
  const searchGraph = async (query: string) => {
    if (!query.trim()) {
      loadGraphData()
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch(`http://localhost:8000/graph/search?query=${encodeURIComponent(query)}&limit=50`)
      if (response.ok) {
        const data = await response.json()
        
        // Validate the data structure before processing
        try {
          validateForReact(data, 'graphSearchResponse')
        } catch (error) {
          console.error('Graph search response validation failed:', error)
          setError('Invalid data structure received from server')
          return
        }
        
        // Clean search result nodes
        const cleanNodes: GraphNode[] = (data.nodes || []).map((node: any) => {
          const cleanProperties: Record<string, string> = {}
          
          if (node.properties && typeof node.properties === 'object') {
            Object.entries(node.properties).forEach(([key, value]) => {
              try {
                if (value === null || value === undefined) {
                  cleanProperties[key] = 'N/A'
                } else if (typeof value === 'string') {
                  cleanProperties[key] = value
                } else if (typeof value === 'number' || typeof value === 'boolean') {
                  cleanProperties[key] = String(value)
                } else if (Array.isArray(value)) {
                  cleanProperties[key] = value.map(v => String(v || 'N/A')).join(', ')
                } else if (typeof value === 'object') {
                  cleanProperties[key] = JSON.stringify(value)
                } else {
                  cleanProperties[key] = String(value)
                }
              } catch (e) {
                cleanProperties[key] = 'Invalid data'
              }
            })
          }
          
          return {
            id: String(node.id || ''),
            label: String(node.label || 'Unknown'),
            type: String(node.type || 'Unknown'),
            properties: cleanProperties
          }
        })
        
        // Clean relationship data
        const cleanEdges: GraphEdge[] = (data.relationships || []).map((edge: any) => ({
          source: String(edge.source || ''),
          target: String(edge.target || ''),
          type: String(edge.type || 'RELATED'),
          properties: {}
        }))
        
        const newGraphData = {
          nodes: cleanNodes,
          edges: cleanEdges
        }
        
        setGraphData(newGraphData)
        
        // Update available types for filtering
        const nodeTypes = Array.from(new Set(cleanNodes.map(n => n.type)))
        const relTypes = Array.from(new Set(cleanEdges.map(e => e.type)))
        setAvailableNodeTypes(nodeTypes)
        setAvailableRelTypes(relTypes)
        
        // Calculate and set statistics
        const graphStats = calculateStats(newGraphData)
        setStats(graphStats)
      } else {
        setError('Search failed')
      }
    } catch (err) {
      console.error('Graph search failed:', err)
      setError('Search unavailable')
    } finally {
      setLoading(false)
    }
  }

  // Load graph statistics
  const loadStats = async () => {
    try {
      const response = await fetch('http://localhost:8000/graph/statistics')
      if (response.ok) {
        const data = await response.json()
        setStats(data.graph_statistics)
      }
    } catch (err) {
      console.error('Stats loading failed:', err)
    }
  }

  // Apply filters when graph data or filters change
  useEffect(() => {
    if (graphData.nodes.length > 0) {
      const filtered = applyFilters(graphData)
      setFilteredData(filtered)
    }
  }, [graphData, applyFilters])

  useEffect(() => {
    loadGraphData()
    loadStats()
  }, [])

  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      if (searchQuery) {
        searchGraph(searchQuery)
      } else {
        loadGraphData()
      }
    }, 500)

    return () => clearTimeout(delayedSearch)
  }, [searchQuery])

  const handleNodeClick = (node: GraphNode) => {
    // Clean node properties to ensure they're all strings for React rendering
    const cleanProperties: Record<string, string> = {}
    
    if (node.properties && typeof node.properties === 'object') {
      Object.entries(node.properties).forEach(([key, value]) => {
        try {
          if (value === null || value === undefined) {
            cleanProperties[key] = 'N/A'
          } else if (typeof value === 'string') {
            cleanProperties[key] = value
          } else if (typeof value === 'number' || typeof value === 'boolean') {
            cleanProperties[key] = String(value)
          } else if (Array.isArray(value)) {
            cleanProperties[key] = value.map(v => String(v || 'N/A')).join(', ')
          } else if (typeof value === 'object') {
            cleanProperties[key] = JSON.stringify(value)
          } else {
            cleanProperties[key] = String(value)
          }
        } catch (e) {
          cleanProperties[key] = 'Invalid data'
        }
      })
    }
    
    const cleanNode: GraphNode = {
      id: String(node.id || ''),
      label: String(node.label || 'Unknown'),
      type: String(node.type || 'Unknown'),
      properties: cleanProperties
    }
    
    setSelectedNode(cleanNode)
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <NetworkIcon className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Knowledge Graph</h1>
            </div>
            <button
              onClick={loadGraphData}
              disabled={loading}
              className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50"
            >
              <RefreshCwIcon className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              <span>Refresh</span>
            </button>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search and Controls */}
        <div className="mb-6">
          <div className="max-w-2xl mx-auto mb-4">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search knowledge graph: entities, publications, relationships..."
              size="large"
            />
          </div>
          
          {/* Control Buttons */}
          <div className="flex justify-center space-x-3 mb-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
                showFilters 
                ? 'bg-primary-100 border-primary-300 text-primary-700' 
                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <FilterIcon className="w-4 h-4" />
              <span>Filters</span>
              {showFilters ? <ChevronUpIcon className="w-4 h-4" /> : <ChevronDownIcon className="w-4 h-4" />}
            </button>
            
            <button
              onClick={() => setShowSettings(!showSettings)}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
                showSettings 
                ? 'bg-primary-100 border-primary-300 text-primary-700' 
                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              <SettingsIcon className="w-4 h-4" />
              <span>Settings</span>
            </button>
            
            <button
              onClick={() => setFilters(prev => ({ ...prev, physics: !prev.physics }))}
              className={`flex items-center space-x-2 px-4 py-2 rounded-lg border ${
                filters.physics 
                ? 'bg-green-100 border-green-300 text-green-700' 
                : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
              }`}
            >
              {filters.physics ? <PauseIcon className="w-4 h-4" /> : <PlayIcon className="w-4 h-4" />}
              <span>{filters.physics ? 'Pause' : 'Play'} Physics</span>
            </button>
          </div>
          
          {/* Filters Panel */}
          {showFilters && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-4">
              <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
                {/* Node Types Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Node Types
                  </label>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {availableNodeTypes.map(type => (
                      <label key={type} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={filters.nodeTypes.includes(type)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFilters(prev => ({ 
                                ...prev, 
                                nodeTypes: [...prev.nodeTypes, type]
                              }))
                            } else {
                              setFilters(prev => ({ 
                                ...prev, 
                                nodeTypes: prev.nodeTypes.filter(t => t !== type)
                              }))
                            }
                          }}
                          className="mr-2 rounded"
                        />
                        <span className="text-sm text-gray-700">{type}</span>
                        <span className="text-xs text-gray-500 ml-1">
                          ({stats?.nodeTypes?.[type] || 0})
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
                
                {/* Relationship Types Filter */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Relationship Types
                  </label>
                  <div className="space-y-2 max-h-32 overflow-y-auto">
                    {availableRelTypes.map(type => (
                      <label key={type} className="flex items-center">
                        <input
                          type="checkbox"
                          checked={filters.relationshipTypes.includes(type)}
                          onChange={(e) => {
                            if (e.target.checked) {
                              setFilters(prev => ({ 
                                ...prev, 
                                relationshipTypes: [...prev.relationshipTypes, type]
                              }))
                            } else {
                              setFilters(prev => ({ 
                                ...prev, 
                                relationshipTypes: prev.relationshipTypes.filter(t => t !== type)
                              }))
                            }
                          }}
                          className="mr-2 rounded"
                        />
                        <span className="text-sm text-gray-700">{type}</span>
                        <span className="text-xs text-gray-500 ml-1">
                          ({stats?.relationshipTypes?.[type] || 0})
                        </span>
                      </label>
                    ))}
                  </div>
                </div>
                
                {/* Numeric Filters */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Min Connections
                  </label>
                  <input
                    type="range"
                    min="0"
                    max="20"
                    value={filters.minConnections}
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      minConnections: parseInt(e.target.value)
                    }))}
                    className="w-full"
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    {filters.minConnections} connections
                  </div>
                  
                  <label className="block text-sm font-medium text-gray-700 mb-2 mt-4">
                    Max Nodes
                  </label>
                  <input
                    type="range"
                    min="10"
                    max="500"
                    step="10"
                    value={filters.maxNodes}
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      maxNodes: parseInt(e.target.value)
                    }))}
                    className="w-full"
                  />
                  <div className="text-xs text-gray-500 mt-1">
                    {filters.maxNodes} nodes max
                  </div>
                </div>
                
                {/* Quick Actions */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Quick Actions
                  </label>
                  <div className="space-y-2">
                    <button
                      onClick={() => setFilters(prev => ({ 
                        ...prev, 
                        nodeTypes: [],
                        relationshipTypes: [],
                        minConnections: 0
                      }))}
                      className="w-full px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200"
                    >
                      Clear Filters
                    </button>
                    <button
                      onClick={() => setFilters(prev => ({ 
                        ...prev, 
                        nodeTypes: availableNodeTypes,
                        relationshipTypes: availableRelTypes
                      }))}
                      className="w-full px-3 py-2 text-sm bg-primary-100 text-primary-700 rounded hover:bg-primary-200"
                    >
                      Select All
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Settings Panel */}
          {showSettings && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 mb-4">
              <div className="grid md:grid-cols-3 gap-6">
                {/* Visual Settings */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Visual Settings</h4>
                  
                  <label className="block text-sm text-gray-700 mb-2">
                    Node Size: {filters.nodeSize}px
                  </label>
                  <input
                    type="range"
                    min="5"
                    max="30"
                    value={filters.nodeSize}
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      nodeSize: parseInt(e.target.value)
                    }))}
                    className="w-full mb-4"
                  />
                  
                  <label className="block text-sm text-gray-700 mb-2">
                    Edge Width: {filters.edgeWidth}px
                  </label>
                  <input
                    type="range"
                    min="1"
                    max="5"
                    value={filters.edgeWidth}
                    onChange={(e) => setFilters(prev => ({ 
                      ...prev, 
                      edgeWidth: parseInt(e.target.value)
                    }))}
                    className="w-full mb-4"
                  />
                  
                  <label className="flex items-center">
                    <input
                      type="checkbox"
                      checked={filters.showLabels}
                      onChange={(e) => setFilters(prev => ({ 
                        ...prev, 
                        showLabels: e.target.checked
                      }))}
                      className="mr-2"
                    />
                    <span className="text-sm text-gray-700">Show Labels</span>
                  </label>
                </div>
                
                {/* Layout Settings */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Layout</h4>
                  <div className="space-y-2">
                    {[
                      { value: 'force', label: 'Force Directed', icon: NetworkIcon },
                      { value: 'circular', label: 'Circular', icon: RotateCcwIcon },
                      { value: 'grid', label: 'Grid', icon: LayoutGridIcon },
                      { value: 'hierarchical', label: 'Hierarchical', icon: BarChart3Icon }
                    ].map(({ value, label, icon: Icon }) => (
                      <label key={value} className="flex items-center">
                        <input
                          type="radio"
                          name="layout"
                          value={value}
                          checked={filters.layout === value}
                          onChange={(e) => setFilters(prev => ({ 
                            ...prev, 
                            layout: e.target.value as any
                          }))}
                          className="mr-2"
                        />
                        <Icon className="w-4 h-4 mr-2 text-gray-500" />
                        <span className="text-sm text-gray-700">{label}</span>
                      </label>
                    ))}
                  </div>
                </div>
                
                {/* Export Options */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-3">Export</h4>
                  <div className="space-y-2">
                    <button className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                      <DownloadIcon className="w-4 h-4" />
                      <span>Export PNG</span>
                    </button>
                    <button className="w-full flex items-center justify-center space-x-2 px-3 py-2 text-sm bg-gray-100 text-gray-700 rounded hover:bg-gray-200">
                      <DownloadIcon className="w-4 h-4" />
                      <span>Export JSON</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          {/* Stats Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
              <div className="flex items-center">
                <NetworkIcon className="w-5 h-5 text-blue-600 mr-2" />
                <div>
                  <p className="text-sm text-gray-600">Nodes</p>
                  <p className="text-xl font-semibold">{filteredData.nodes.length}</p>
                  {filteredData.nodes.length !== graphData.nodes.length && (
                    <p className="text-xs text-gray-500">of {graphData.nodes.length} total</p>
                  )}
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
              <div className="flex items-center">
                <BarChart3Icon className="w-5 h-5 text-green-600 mr-2" />
                <div>
                  <p className="text-sm text-gray-600">Relationships</p>
                  <p className="text-xl font-semibold">{filteredData.edges.length}</p>
                  {filteredData.edges.length !== graphData.edges.length && (
                    <p className="text-xs text-gray-500">of {graphData.edges.length} total</p>
                  )}
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
              <div className="flex items-center">
                <InfoIcon className="w-5 h-5 text-purple-600 mr-2" />
                <div>
                  <p className="text-sm text-gray-600">Publications</p>
                  <p className="text-xl font-semibold">
                    {stats?.nodeTypes?.['Publication'] || 0}
                  </p>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
              <div className="flex items-center">
                <SearchIcon className="w-5 h-5 text-orange-600 mr-2" />
                <div>
                  <p className="text-sm text-gray-600">Entities</p>
                  <p className="text-xl font-semibold">
                    {stats?.nodeTypes?.['Entity'] || 0}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-4 gap-6">
          {/* Graph Visualization */}
          <div className="lg:col-span-3">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900">Graph Visualization</h2>
                {loading && (
                  <div className="flex items-center text-sm text-gray-600">
                    <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin mr-2"></div>
                    Loading...
                  </div>
                )}
              </div>
              
              {error ? (
                <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                  <p className="text-red-600 font-medium mb-2">Graph Unavailable</p>
                  <p className="text-red-700 text-sm">{error}</p>
                  <button 
                    onClick={loadGraphData}
                    className="mt-3 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
                  >
                    Retry
                  </button>
                </div>
              ) : filteredData.nodes.length === 0 && !loading ? (
                <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                  <NetworkIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                  <h3 className="text-lg font-medium text-gray-900 mb-2">No Graph Data</h3>
                  <p className="text-gray-600 mb-4">
                    {searchQuery ? 'No results found for your search.' : 'No knowledge graph data available.'}
                  </p>
                  <p className="text-sm text-gray-500">
                    Ensure the backend is connected to Neo4j database with data.
                  </p>
                </div>
              ) : (
                <ErrorBoundary>
                <GraphVisualization
                  nodes={filteredData.nodes.map(node => ({
                    ...node,
                    id: safeRender(node.id || ''),
                    label: safeRender(node.label || 'Unknown'),
                    type: safeRender(node.type || 'Unknown'),
                    properties: Object.fromEntries(
                      Object.entries(node.properties || {}).map(([k, v]) => [k, safeRender(v || 'N/A')])
                    )
                  }))}
                  edges={filteredData.edges.map(edge => ({
                    ...edge,
                    source: safeRender(edge.source || ''),
                    target: safeRender(edge.target || ''),
                    type: safeRender(edge.type || 'RELATED'),
                    properties: Object.fromEntries(
                      Object.entries(edge.properties || {}).map(([k, v]) => [k, safeRender(v || 'N/A')])
                    )
                  }))}
                  width={800}
                  height={600}
                  onNodeClick={handleNodeClick}
                  layout={filters.layout}
                  nodeSize={filters.nodeSize}
                  edgeWidth={filters.edgeWidth}
                  showLabels={filters.showLabels}
                  physics={filters.physics}
                />
                </ErrorBoundary>
              )}
            </div>
          </div>

          {/* Node Details Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Node Details</h3>
              
              {selectedNode ? (
                <div className="space-y-4">
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">{selectedNode.label}</h4>
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                      {selectedNode.type}
                    </span>
                  </div>
                  
                  <div>
                    <h5 className="text-sm font-medium text-gray-700 mb-2">Properties</h5>
                    <div className="space-y-2">
                      {Object.entries(selectedNode.properties).slice(0, 8).map(([key, value]) => {
                        // Use safe rendering for all property values
                        const displayValue = safeRender(value);
                        const truncatedValue = displayValue.length > 50 ? displayValue.substring(0, 50) + '...' : displayValue;
                        
                        return (
                          <ErrorBoundary key={key}>
                          <div className="text-xs">
                            <span className="font-medium text-gray-600">{safeRender(key)}:</span>
                            <span className="text-gray-800 ml-1">{truncatedValue}</span>
                          </div>
                          </ErrorBoundary>
                        );
                      })}
                    </div>
                  </div>
                  
                  <button className="w-full px-3 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 text-sm">
                    Explore Connections
                  </button>
                </div>
              ) : (
                <div className="text-center text-gray-500">
                  <NetworkIcon className="w-8 h-8 mx-auto mb-2 opacity-50" />
                  <p className="text-sm">Click on a node to view details</p>
                </div>
              )}
            </div>

            {/* Node Type Legend */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 mt-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Node Types</h3>
              <div className="space-y-2">
                {Array.from(new Set(filteredData.nodes.map(n => n.type))).map(type => (
                  <div key={type} className="flex items-center gap-2 text-sm">
                    <div 
                      className="w-3 h-3 rounded-full"
                      style={{ 
                        backgroundColor: 
                          type === 'Publication' ? '#3b82f6' :
                          type === 'Entity' ? '#10b981' :
                          type === 'Page' ? '#8b5cf6' :
                          type === 'Author' ? '#f59e0b' :
                          type === 'Organism' ? '#06b6d4' :
                          type === 'Gene' ? '#ef4444' :
                          type === 'Protein' ? '#6366f1' : '#6b7280'
                      }}
                    ></div>
                    <span className="text-gray-700">{type}</span>
                    <span className="text-gray-500 text-xs">
                      ({filteredData.nodes.filter(n => n.type === type).length})
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}