'use client'

import React, { useEffect, useRef, useState, useCallback } from 'react'

interface GraphNode {
  id: string
  label: string
  type: string
  x?: number
  y?: number
  properties: Record<string, any>
}

interface GraphEdge {
  source: string
  target: string
  type: string
  properties: Record<string, any>
}

interface GraphVisualizationProps {
  nodes: GraphNode[]
  edges: GraphEdge[]
  width: number
  height: number
  onNodeClick?: (node: GraphNode) => void
  layout?: 'force' | 'circular' | 'grid' | 'hierarchical'
  nodeSize?: number
  edgeWidth?: number
  showLabels?: boolean
  physics?: boolean
}

export function GraphVisualization({ 
  nodes, 
  edges, 
  width, 
  height, 
  onNodeClick,
  layout = 'force',
  nodeSize = 15,
  edgeWidth = 1,
  showLabels = true,
  physics = true
}: GraphVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const animationRef = useRef<number>()
  const [processedNodes, setProcessedNodes] = useState<GraphNode[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [draggedNode, setDraggedNode] = useState<GraphNode | null>(null)
  const [hoveredNode, setHoveredNode] = useState<GraphNode | null>(null)
  const [zoom, setZoom] = useState(1)
  const [pan, setPan] = useState({ x: 0, y: 0 })
  const [forces, setForces] = useState<Map<string, { vx: number; vy: number }>>(new Map())

  // Layout algorithms
  const applyLayout = useCallback((layoutType: string, nodesList: GraphNode[]) => {
    const centerX = width / 2
    const centerY = height / 2
    const maxRadius = Math.min(width, height) * 0.4

    switch (layoutType) {
      case 'circular':
        return nodesList.map((node, index) => {
          const angle = (2 * Math.PI * index) / nodesList.length
          return {
            ...node,
            x: centerX + maxRadius * Math.cos(angle),
            y: centerY + maxRadius * Math.sin(angle)
          }
        })

      case 'grid':
        const cols = Math.ceil(Math.sqrt(nodesList.length))
        const spacing = Math.min(width, height) / (cols + 1)
        return nodesList.map((node, index) => {
          const row = Math.floor(index / cols)
          const col = index % cols
          return {
            ...node,
            x: spacing * (col + 1),
            y: spacing * (row + 1)
          }
        })

      case 'hierarchical':
        const levels = new Map<string, number>()
        const nodeTypes = Array.from(new Set(nodesList.map(n => n.type)))
        nodeTypes.forEach((type, index) => levels.set(type, index))
        
        return nodesList.map((node, index) => {
          const level = levels.get(node.type) || 0
          const nodesAtLevel = nodesList.filter(n => n.type === node.type)
          const indexAtLevel = nodesAtLevel.indexOf(node)
          const levelSpacing = height / (nodeTypes.length + 1)
          const nodeSpacing = width / (nodesAtLevel.length + 1)
          
          return {
            ...node,
            x: nodeSpacing * (indexAtLevel + 1),
            y: levelSpacing * (level + 1)
          }
        })

      case 'force':
      default:
        // Initialize with random positions for force simulation
        return nodesList.map(node => ({
          ...node,
          x: centerX + (Math.random() - 0.5) * maxRadius,
          y: centerY + (Math.random() - 0.5) * maxRadius
        }))
    }
  }, [width, height])

  // Force simulation for physics-based layout
  const applyForces = useCallback(() => {
    if (!physics || layout !== 'force') return

    setProcessedNodes(prevNodes => {
      const newNodes = [...prevNodes]
      const newForces = new Map(forces)

      // Repulsion force between nodes
      for (let i = 0; i < newNodes.length; i++) {
        for (let j = i + 1; j < newNodes.length; j++) {
          const nodeA = newNodes[i]
          const nodeB = newNodes[j]
          
          if (!nodeA.x || !nodeA.y || !nodeB.x || !nodeB.y) continue

          const dx = nodeB.x - nodeA.x
          const dy = nodeB.y - nodeA.y
          const distance = Math.sqrt(dx * dx + dy * dy) || 1
          const force = 1000 / (distance * distance)
          const fx = (dx / distance) * force
          const fy = (dy / distance) * force

          const forceA = newForces.get(nodeA.id) || { vx: 0, vy: 0 }
          const forceB = newForces.get(nodeB.id) || { vx: 0, vy: 0 }

          newForces.set(nodeA.id, { vx: forceA.vx - fx, vy: forceA.vy - fy })
          newForces.set(nodeB.id, { vx: forceB.vx + fx, vy: forceB.vy + fy })
        }
      }

      // Attraction force for connected nodes
      edges.forEach(edge => {
        const sourceNode = newNodes.find(n => n.id === edge.source)
        const targetNode = newNodes.find(n => n.id === edge.target)
        
        if (!sourceNode || !targetNode || !sourceNode.x || !sourceNode.y || !targetNode.x || !targetNode.y) return

        const dx = targetNode.x - sourceNode.x
        const dy = targetNode.y - sourceNode.y
        const distance = Math.sqrt(dx * dx + dy * dy) || 1
        const desiredDistance = 100
        const force = (distance - desiredDistance) * 0.1
        const fx = (dx / distance) * force
        const fy = (dy / distance) * force

        const forceSource = newForces.get(sourceNode.id) || { vx: 0, vy: 0 }
        const forceTarget = newForces.get(targetNode.id) || { vx: 0, vy: 0 }

        newForces.set(sourceNode.id, { vx: forceSource.vx + fx, vy: forceSource.vy + fy })
        newForces.set(targetNode.id, { vx: forceTarget.vx - fx, vy: forceTarget.vy - fy })
      })

      // Apply forces and damping
      newNodes.forEach(node => {
        if (!node.x || !node.y) return
        
        const force = newForces.get(node.id) || { vx: 0, vy: 0 }
        const damping = 0.85
        
        force.vx *= damping
        force.vy *= damping
        
        node.x += force.vx * 0.01
        node.y += force.vy * 0.01

        // Keep nodes within bounds
        const margin = nodeSize * 2
        node.x = Math.max(margin, Math.min(width - margin, node.x))
        node.y = Math.max(margin, Math.min(height - margin, node.y))
      })

      setForces(newForces)
      return newNodes
    })
  }, [physics, layout, edges, forces, width, height, nodeSize])

  // Initialize node positions
  useEffect(() => {
    if (nodes.length === 0) return

    const nodesWithPositions = applyLayout(layout, nodes)
    setProcessedNodes(nodesWithPositions)
    
    // Initialize forces for each node
    const initialForces = new Map<string, { vx: number; vy: number }>()
    nodes.forEach(node => {
      initialForces.set(node.id, { vx: 0, vy: 0 })
    })
    setForces(initialForces)
  }, [nodes, layout, applyLayout])

  // Animation loop for physics
  useEffect(() => {
    if (physics && layout === 'force') {
      const animate = () => {
        applyForces()
        animationRef.current = requestAnimationFrame(animate)
      }
      animationRef.current = requestAnimationFrame(animate)
    }

    return () => {
      if (animationRef.current) {
        cancelAnimationFrame(animationRef.current)
      }
    }
  }, [physics, layout, applyForces])

  // Enhanced drawing with better visual effects
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || processedNodes.length === 0) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Apply zoom and pan transformations
    ctx.save()
    ctx.scale(zoom, zoom)
    ctx.translate(pan.x, pan.y)

    // Clear canvas with gradient background
    ctx.clearRect(-pan.x / zoom, -pan.y / zoom, width / zoom, height / zoom)
    
    // Draw subtle grid pattern
    ctx.strokeStyle = 'rgba(148, 163, 184, 0.1)'
    ctx.lineWidth = 0.5
    const gridSize = 50
    for (let x = 0; x < width; x += gridSize) {
      ctx.beginPath()
      ctx.moveTo(x, 0)
      ctx.lineTo(x, height)
      ctx.stroke()
    }
    for (let y = 0; y < height; y += gridSize) {
      ctx.beginPath()
      ctx.moveTo(0, y)
      ctx.lineTo(width, y)
      ctx.stroke()
    }

    // Draw edges with improved styling
    edges.forEach(edge => {
      const sourceNode = processedNodes.find(n => n.id === edge.source)
      const targetNode = processedNodes.find(n => n.id === edge.target)
      
      if (sourceNode && targetNode && sourceNode.x !== undefined && sourceNode.y !== undefined && targetNode.x !== undefined && targetNode.y !== undefined) {
        // Edge color based on type
        const edgeColors: Record<string, string> = {
          'MENTIONED_IN': '#8b5cf6',
          'AUTHORED_BY': '#f59e0b',
          'RELATED_TO': '#10b981',
          'CONTAINS': '#3b82f6',
          'default': '#94a3b8'
        }
        
        const color = edgeColors[edge.type] || edgeColors.default
        
        // Draw curved edge
        ctx.strokeStyle = color
        ctx.lineWidth = edgeWidth
        ctx.globalAlpha = 0.6
        
        const dx = targetNode.x - sourceNode.x
        const dy = targetNode.y - sourceNode.y
        const distance = Math.sqrt(dx * dx + dy * dy)
        
        // Calculate curve control point
        const controlX = (sourceNode.x + targetNode.x) / 2 + dy * 0.2
        const controlY = (sourceNode.y + targetNode.y) / 2 - dx * 0.2
        
        ctx.beginPath()
        ctx.moveTo(sourceNode.x, sourceNode.y)
        ctx.quadraticCurveTo(controlX, controlY, targetNode.x, targetNode.y)
        ctx.stroke()
        
        // Draw arrowhead
        const angle = Math.atan2(dy, dx)
        const arrowLength = 8
        const arrowWidth = 4
        
        const endX = targetNode.x - Math.cos(angle) * nodeSize
        const endY = targetNode.y - Math.sin(angle) * nodeSize
        
        ctx.fillStyle = color
        ctx.beginPath()
        ctx.moveTo(endX, endY)
        ctx.lineTo(
          endX - arrowLength * Math.cos(angle - Math.PI / 6),
          endY - arrowLength * Math.sin(angle - Math.PI / 6)
        )
        ctx.lineTo(
          endX - arrowLength * Math.cos(angle + Math.PI / 6),
          endY - arrowLength * Math.sin(angle + Math.PI / 6)
        )
        ctx.closePath()
        ctx.fill()
        
        ctx.globalAlpha = 1
      }
    })

    // Draw nodes with enhanced styling
    processedNodes.forEach(node => {
      if (node.x === undefined || node.y === undefined) return

      const isHovered = hoveredNode?.id === node.id
      const currentNodeSize = isHovered ? nodeSize * 1.3 : nodeSize

      // Node color based on type with better palette
      const nodeColors: Record<string, { primary: string; secondary: string }> = {
        'Publication': { primary: '#3b82f6', secondary: '#93c5fd' },
        'Entity': { primary: '#10b981', secondary: '#6ee7b7' },
        'Page': { primary: '#8b5cf6', secondary: '#c4b5fd' },
        'Author': { primary: '#f59e0b', secondary: '#fcd34d' },
        'Organism': { primary: '#06b6d4', secondary: '#67e8f9' },
        'Gene': { primary: '#ef4444', secondary: '#fca5a5' },
        'Protein': { primary: '#6366f1', secondary: '#a5b4fc' },
        'default': { primary: '#6b7280', secondary: '#d1d5db' }
      }

      const colors = nodeColors[node.type] || nodeColors.default

      // Draw node shadow
      ctx.shadowColor = 'rgba(0, 0, 0, 0.2)'
      ctx.shadowBlur = isHovered ? 15 : 8
      ctx.shadowOffsetX = 2
      ctx.shadowOffsetY = 2

      // Draw node gradient
      const gradient = ctx.createRadialGradient(
        node.x - currentNodeSize / 3, 
        node.y - currentNodeSize / 3, 
        0,
        node.x, 
        node.y, 
        currentNodeSize
      )
      gradient.addColorStop(0, colors.secondary)
      gradient.addColorStop(1, colors.primary)

      ctx.fillStyle = gradient
      ctx.beginPath()
      ctx.arc(node.x, node.y, currentNodeSize, 0, 2 * Math.PI)
      ctx.fill()

      // Reset shadow
      ctx.shadowColor = 'transparent'
      ctx.shadowBlur = 0
      ctx.shadowOffsetX = 0
      ctx.shadowOffsetY = 0

      // Draw node border
      ctx.strokeStyle = isHovered ? '#ffffff' : 'rgba(255, 255, 255, 0.8)'
      ctx.lineWidth = isHovered ? 3 : 2
      ctx.stroke()

      // Draw node icon or initial
      ctx.fillStyle = '#ffffff'
      ctx.font = `bold ${currentNodeSize * 0.6}px sans-serif`
      ctx.textAlign = 'center'
      ctx.textBaseline = 'middle'
      
      const icon = node.type.charAt(0).toUpperCase()
      ctx.fillText(icon, node.x, node.y)

      // Draw node label
      if (showLabels) {
        ctx.fillStyle = isHovered ? '#1f2937' : '#4b5563'
        ctx.font = isHovered ? 'bold 13px sans-serif' : '12px sans-serif'
        ctx.textAlign = 'center'
        ctx.textBaseline = 'top'
        
        const label = node.label.length > 20 ? node.label.substring(0, 20) + '...' : node.label
        const labelY = node.y + currentNodeSize + 8
        
        // Draw label background for better readability
        const labelWidth = ctx.measureText(label).width
        ctx.fillStyle = 'rgba(255, 255, 255, 0.9)'
        ctx.fillRect(node.x - labelWidth / 2 - 4, labelY - 2, labelWidth + 8, 16)
        
        ctx.fillStyle = isHovered ? '#1f2937' : '#4b5563'
        ctx.fillText(label, node.x, labelY)
      }
    })

    ctx.restore()
  }, [processedNodes, edges, width, height, zoom, pan, hoveredNode, nodeSize, edgeWidth, showLabels])

  // Enhanced mouse interaction handling
  const getMousePosition = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return { x: 0, y: 0 }

    const rect = canvas.getBoundingClientRect()
    const x = (event.clientX - rect.left - pan.x) / zoom
    const y = (event.clientY - rect.top - pan.y) / zoom
    
    return { x, y }
  }

  const findNodeAtPosition = (x: number, y: number) => {
    return processedNodes.find(node => {
      if (node.x === undefined || node.y === undefined) return false
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
      return distance <= nodeSize
    })
  }

  const handleMouseDown = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getMousePosition(event)
    const clickedNode = findNodeAtPosition(x, y)

    if (clickedNode) {
      setIsDragging(true)
      setDraggedNode(clickedNode)
      onNodeClick?.(clickedNode)
      
      // Stop physics for dragged node
      if (physics && layout === 'force') {
        setForces(prev => {
          const newForces = new Map(prev)
          newForces.set(clickedNode.id, { vx: 0, vy: 0 })
          return newForces
        })
      }
    }
  }

  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const { x, y } = getMousePosition(event)
    
    // Handle node hovering
    const hoveredNode = findNodeAtPosition(x, y)
    setHoveredNode(hoveredNode)
    
    // Change cursor based on hover state
    const canvas = canvasRef.current
    if (canvas) {
      canvas.style.cursor = hoveredNode ? 'pointer' : isDragging ? 'grabbing' : 'grab'
    }

    // Handle dragging
    if (isDragging && draggedNode) {
      setProcessedNodes(nodes => 
        nodes.map(node => 
          node.id === draggedNode.id 
            ? { ...node, x, y }
            : node
        )
      )
    }
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    setDraggedNode(null)
  }

  const handleMouseLeave = () => {
    setHoveredNode(null)
    setIsDragging(false)
    setDraggedNode(null)
  }

  // Zoom and pan functionality
  const handleWheel = (event: React.WheelEvent<HTMLCanvasElement>) => {
    event.preventDefault()
    const zoomFactor = event.deltaY > 0 ? 0.9 : 1.1
    const newZoom = Math.max(0.1, Math.min(3, zoom * zoomFactor))
    setZoom(newZoom)
  }

  return (
    <div className="relative bg-gradient-to-br from-gray-50 to-gray-100 rounded-lg overflow-hidden">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseLeave}
        onWheel={handleWheel}
        className="block cursor-grab active:cursor-grabbing"
        style={{ 
          display: 'block',
          background: 'linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)'
        }}
      />
      
      {/* Zoom Controls */}
      <div className="absolute top-4 left-4 flex flex-col space-y-2">
        <button
          onClick={() => setZoom(Math.min(3, zoom * 1.2))}
          className="w-8 h-8 bg-white rounded-full shadow-sm border border-gray-200 flex items-center justify-center hover:bg-gray-50 transition-colors"
          title="Zoom In"
        >
          <span className="text-gray-600 text-lg font-bold">+</span>
        </button>
        <button
          onClick={() => setZoom(Math.max(0.1, zoom * 0.8))}
          className="w-8 h-8 bg-white rounded-full shadow-sm border border-gray-200 flex items-center justify-center hover:bg-gray-50 transition-colors"
          title="Zoom Out"
        >
          <span className="text-gray-600 text-lg font-bold">−</span>
        </button>
        <button
          onClick={() => {
            setZoom(1)
            setPan({ x: 0, y: 0 })
          }}
          className="w-8 h-8 bg-white rounded-full shadow-sm border border-gray-200 flex items-center justify-center hover:bg-gray-50 transition-colors text-xs font-medium"
          title="Reset View"
        >
          ⌂
        </button>
      </div>

      {/* Graph Statistics */}
      <div className="absolute bottom-4 left-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-sm border border-gray-200">
        <div className="text-xs text-gray-600">
          <div>Nodes: <span className="font-semibold text-gray-900">{nodes.length}</span></div>
          <div>Edges: <span className="font-semibold text-gray-900">{edges.length}</span></div>
          <div>Zoom: <span className="font-semibold text-gray-900">{Math.round(zoom * 100)}%</span></div>
        </div>
      </div>
      
      {/* Enhanced Legend */}
      <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm p-4 rounded-lg shadow-lg border border-gray-200 max-w-xs">
        <h4 className="font-semibold text-sm text-gray-900 mb-3 flex items-center">
          <div className="w-2 h-2 bg-primary-500 rounded-full mr-2"></div>
          Node Types
        </h4>
        <div className="space-y-2 max-h-40 overflow-y-auto">
          {Array.from(new Set(nodes.map(n => n.type))).map(type => {
            const count = nodes.filter(n => n.type === type).length
            const colors = {
              'Publication': { primary: '#3b82f6', secondary: '#93c5fd' },
              'Entity': { primary: '#10b981', secondary: '#6ee7b7' },
              'Page': { primary: '#8b5cf6', secondary: '#c4b5fd' },
              'Author': { primary: '#f59e0b', secondary: '#fcd34d' },
              'Organism': { primary: '#06b6d4', secondary: '#67e8f9' },
              'Gene': { primary: '#ef4444', secondary: '#fca5a5' },
              'Protein': { primary: '#6366f1', secondary: '#a5b4fc' },
              'default': { primary: '#6b7280', secondary: '#d1d5db' }
            }
            const color = colors[type as keyof typeof colors] || colors.default
            
            return (
              <div key={type} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <div 
                    className="w-4 h-4 rounded-full shadow-sm border border-white flex items-center justify-center text-white font-bold text-xs"
                    style={{ 
                      background: `linear-gradient(135deg, ${color.secondary} 0%, ${color.primary} 100%)`
                    }}
                  >
                    {type.charAt(0)}
                  </div>
                  <span className="text-gray-700 font-medium">{type}</span>
                </div>
                <span className="text-gray-500 bg-gray-100 px-2 py-0.5 rounded-full text-xs font-medium">
                  {count}
                </span>
              </div>
            )
          })}
        </div>
        
        {hoveredNode && (
          <div className="mt-3 pt-3 border-t border-gray-200">
            <h5 className="font-medium text-xs text-gray-900 mb-1">Hovered Node</h5>
            <div className="text-xs text-gray-600">
              <div className="font-medium">{hoveredNode.label}</div>
              <div className="text-gray-500">{hoveredNode.type}</div>
            </div>
          </div>
        )}
      </div>
      
      {/* Layout Indicator */}
      <div className="absolute bottom-4 right-4 bg-white/90 backdrop-blur-sm rounded-lg px-3 py-2 shadow-sm border border-gray-200">
        <div className="text-xs text-gray-600 flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${physics ? 'bg-green-500' : 'bg-gray-400'}`}></div>
          <span className="font-medium">{layout} layout</span>
          {physics && <span className="text-gray-500">• physics on</span>}
        </div>
      </div>
    </div>
  )
}