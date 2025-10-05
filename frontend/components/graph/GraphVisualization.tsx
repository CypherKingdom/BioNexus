'use client'

import React, { useEffect, useRef, useState } from 'react'

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
}

export function GraphVisualization({ nodes, edges, width, height, onNodeClick }: GraphVisualizationProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const [processedNodes, setProcessedNodes] = useState<GraphNode[]>([])
  const [isDragging, setIsDragging] = useState(false)
  const [draggedNode, setDraggedNode] = useState<GraphNode | null>(null)

  // Initialize node positions
  useEffect(() => {
    if (nodes.length === 0) return

    const nodesWithPositions = nodes.map((node, index) => {
      // Simple circular layout
      const angle = (2 * Math.PI * index) / nodes.length
      const radius = Math.min(width, height) * 0.3
      const centerX = width / 2
      const centerY = height / 2

      return {
        ...node,
        x: centerX + radius * Math.cos(angle),
        y: centerY + radius * Math.sin(angle)
      }
    })

    setProcessedNodes(nodesWithPositions)
  }, [nodes, width, height])

  // Draw the graph
  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas || processedNodes.length === 0) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, width, height)

    // Draw edges
    ctx.strokeStyle = '#94a3b8'
    ctx.lineWidth = 1
    
    edges.forEach(edge => {
      const sourceNode = processedNodes.find(n => n.id === edge.source)
      const targetNode = processedNodes.find(n => n.id === edge.target)
      
      if (sourceNode && targetNode && sourceNode.x !== undefined && sourceNode.y !== undefined && targetNode.x !== undefined && targetNode.y !== undefined) {
        ctx.beginPath()
        ctx.moveTo(sourceNode.x, sourceNode.y)
        ctx.lineTo(targetNode.x, targetNode.y)
        ctx.stroke()

        // Draw edge label
        const midX = (sourceNode.x + targetNode.x) / 2
        const midY = (sourceNode.y + targetNode.y) / 2
        ctx.fillStyle = '#64748b'
        ctx.font = '10px sans-serif'
        ctx.textAlign = 'center'
        ctx.fillText(edge.type, midX, midY)
      }
    })

    // Draw nodes
    processedNodes.forEach(node => {
      if (node.x === undefined || node.y === undefined) return

      // Node color based on type
      const nodeColors: Record<string, string> = {
        'Publication': '#3b82f6',
        'Entity': '#10b981',
        'Page': '#8b5cf6',
        'Author': '#f59e0b',
        'Organism': '#06b6d4',
        'Gene': '#ef4444',
        'Protein': '#6366f1',
        'default': '#6b7280'
      }

      const color = nodeColors[node.type] || nodeColors.default

      // Draw node circle
      ctx.fillStyle = color
      ctx.beginPath()
      ctx.arc(node.x, node.y, 15, 0, 2 * Math.PI)
      ctx.fill()

      // Draw node border
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 2
      ctx.stroke()

      // Draw node label
      ctx.fillStyle = '#1f2937'
      ctx.font = '12px sans-serif'
      ctx.textAlign = 'center'
      const label = node.label.length > 20 ? node.label.substring(0, 20) + '...' : node.label
      ctx.fillText(label, node.x, node.y + 30)
    })
  }, [processedNodes, edges, width, height])

  // Handle mouse events
  const handleMouseDown = (event: React.MouseEvent<HTMLCanvasElement>) => {
    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    // Find clicked node
    const clickedNode = processedNodes.find(node => {
      if (node.x === undefined || node.y === undefined) return false
      const distance = Math.sqrt((x - node.x) ** 2 + (y - node.y) ** 2)
      return distance <= 15
    })

    if (clickedNode) {
      setIsDragging(true)
      setDraggedNode(clickedNode)
      onNodeClick?.(clickedNode)
    }
  }

  const handleMouseMove = (event: React.MouseEvent<HTMLCanvasElement>) => {
    if (!isDragging || !draggedNode) return

    const canvas = canvasRef.current
    if (!canvas) return

    const rect = canvas.getBoundingClientRect()
    const x = event.clientX - rect.left
    const y = event.clientY - rect.top

    // Update dragged node position
    setProcessedNodes(nodes => 
      nodes.map(node => 
        node.id === draggedNode.id 
          ? { ...node, x, y }
          : node
      )
    )
  }

  const handleMouseUp = () => {
    setIsDragging(false)
    setDraggedNode(null)
  }

  return (
    <div className="relative">
      <canvas
        ref={canvasRef}
        width={width}
        height={height}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        onMouseLeave={handleMouseUp}
        className="border border-gray-200 rounded-lg cursor-pointer"
        style={{ display: 'block' }}
      />
      
      {/* Legend */}
      <div className="absolute top-4 right-4 bg-white p-3 rounded-lg shadow-sm border border-gray-200">
        <h4 className="font-medium text-sm text-gray-900 mb-2">Node Types</h4>
        <div className="space-y-1">
          {Array.from(new Set(nodes.map(n => n.type))).map(type => (
            <div key={type} className="flex items-center gap-2 text-xs">
              <div 
                className={`w-3 h-3 rounded-full`}
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
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}