'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Download, 
  Database, 
  FileText, 
  Network, 
  Brain, 
  Server,
  CheckCircle,
  Clock,
  AlertCircle,
  ExternalLink
} from 'lucide-react'

interface ExportFormat {
  id: string
  name: string
  description: string
  format: string
  size: string
  status: 'available' | 'generating' | 'unavailable'
  dataTypes: string[]
}

export const ExportSystem: React.FC = () => {
  const [selectedFormats, setSelectedFormats] = useState<string[]>([])
  
  const exportFormats: ExportFormat[] = [
    {
      id: 'knowledge-graph',
      name: 'Neo4j Knowledge Graph',
      description: 'Complete research relationship graph with entities and connections',
      format: 'GraphML / Cypher',
      size: '2.3 GB',
      status: 'available',
      dataTypes: ['Entities', 'Relationships', 'Publications', 'Metadata']
    },
    {
      id: 'vector-embeddings',
      name: 'ColPali Vector Embeddings',
      description: 'High-dimensional semantic embeddings for similarity search',
      format: 'NPY / HDF5',
      size: '1.8 GB',
      status: 'available',
      dataTypes: ['Document Embeddings', 'Image Embeddings', 'Metadata']
    },
    {
      id: 'research-summaries',
      name: 'Research Summaries',
      description: 'AI-generated summaries and key findings from all publications',
      format: 'JSON / CSV',
      size: '45 MB',
      status: 'available',
      dataTypes: ['Summaries', 'Key Findings', 'Citations', 'Topics']
    },
    {
      id: 'biomedical-entities',
      name: 'Biomedical Entities',
      description: 'Extracted organisms, genes, proteins, and experimental conditions',
      format: 'JSON / TSV',
      size: '128 MB',
      status: 'available',
      dataTypes: ['Species', 'Genes', 'Proteins', 'Conditions', 'Endpoints']
    },
    {
      id: 'mission-reports',
      name: 'Mission Planning Reports',
      description: 'Generated mission planning analysis and recommendations',
      format: 'PDF / DOCX',
      size: '23 MB',
      status: 'generating',
      dataTypes: ['Requirements', 'Risk Analysis', 'Recommendations']
    },
    {
      id: 'api-endpoints',
      name: 'API Access Documentation',
      description: 'Complete API documentation and programmatic access guides',
      format: 'OpenAPI / Markdown',
      size: '5 MB',
      status: 'available',
      dataTypes: ['Endpoints', 'Schemas', 'Examples', 'Authentication']
    }
  ]

  const pipelineIntegration = [
    {
      component: 'Ingestion Pipeline',
      icon: <FileText className="w-5 h-5" />,
      status: 'active',
      description: 'Processing 608 NASA bioscience publications',
      exports: ['Raw Text', 'Metadata', 'Processing Logs']
    },
    {
      component: 'OCR Engine',
      icon: <Brain className="w-5 h-5" />,
      status: 'active',
      description: 'Text extraction from document images',
      exports: ['OCR Text', 'Confidence Scores', 'Image Regions']
    },
    {
      component: 'Vector Database',
      icon: <Server className="w-5 h-5" />,
      status: 'active',
      description: 'FAISS similarity search index',
      exports: ['Vector Index', 'Similarity Matrices', 'Search Results']
    },
    {
      component: 'Knowledge Graph',
      icon: <Network className="w-5 h-5" />,
      status: 'active',
      description: 'Neo4j graph database',
      exports: ['Graph Data', 'Query Results', 'Analytics']
    }
  ]

  const handleFormatToggle = (formatId: string) => {
    setSelectedFormats(prev => 
      prev.includes(formatId) 
        ? prev.filter(id => id !== formatId)
        : [...prev, formatId]
    )
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'available':
        return <CheckCircle className="w-4 h-4 text-green-500" />
      case 'generating':
        return <Clock className="w-4 h-4 text-yellow-500 animate-pulse" />
      case 'unavailable':
        return <AlertCircle className="w-4 h-4 text-red-500" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'available':
        return 'bg-green-100 text-green-800'
      case 'generating':
        return 'bg-yellow-100 text-yellow-800'
      case 'unavailable':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  return (
    <div className="space-y-6">
      {/* Export Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Download className="w-5 h-5 text-blue-600" />
            BioNexus Export System
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-blue-50 rounded-lg">
              <Database className="w-8 h-8 text-blue-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Total Data Size</p>
              <p className="text-lg font-bold text-blue-600">4.3 GB</p>
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg">
              <CheckCircle className="w-8 h-8 text-green-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Available Exports</p>
              <p className="text-lg font-bold text-green-600">5/6</p>
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg">
              <Network className="w-8 h-8 text-purple-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Format Types</p>
              <p className="text-lg font-bold text-purple-600">12</p>
            </div>
            <div className="text-center p-4 bg-orange-50 rounded-lg">
              <FileText className="w-8 h-8 text-orange-600 mx-auto mb-2" />
              <p className="text-sm font-medium">Publications</p>
              <p className="text-lg font-bold text-orange-600">608</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Pipeline Integration Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Server className="w-5 h-5 text-purple-600" />
            Pipeline Integration Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-2 gap-4">
            {pipelineIntegration.map((component, index) => (
              <div key={index} className="border rounded-lg p-4">
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    {component.icon}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-medium text-gray-900">{component.component}</h4>
                    <p className="text-sm text-gray-600">{component.description}</p>
                  </div>
                  <Badge className="bg-green-100 text-green-800">
                    {component.status}
                  </Badge>
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-medium text-gray-700">Available Exports:</p>
                  <div className="flex flex-wrap gap-1">
                    {component.exports.map((exportType, exportIndex) => (
                      <Badge key={exportIndex} variant="secondary" className="text-xs">
                        {exportType}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Export Formats */}
      <Card>
        <CardHeader>
          <CardTitle>Available Export Formats</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {exportFormats.map((format) => (
              <div
                key={format.id}
                className={`border rounded-lg p-4 cursor-pointer transition-colors ${
                  selectedFormats.includes(format.id)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => handleFormatToggle(format.id)}
              >
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <input
                      type="checkbox"
                      checked={selectedFormats.includes(format.id)}
                      onChange={() => handleFormatToggle(format.id)}
                      className="h-4 w-4 text-blue-600"
                      disabled={format.status === 'unavailable'}
                    />
                    <div>
                      <h4 className="font-medium text-gray-900">{format.name}</h4>
                      <p className="text-sm text-gray-600">{format.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(format.status)}
                    <Badge variant="outline" className={getStatusColor(format.status)}>
                      {format.status}
                    </Badge>
                  </div>
                </div>
                
                <div className="grid md:grid-cols-3 gap-4 text-sm">
                  <div>
                    <p className="font-medium text-gray-700">Format:</p>
                    <p className="text-gray-600">{format.format}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Size:</p>
                    <p className="text-gray-600">{format.size}</p>
                  </div>
                  <div>
                    <p className="font-medium text-gray-700">Data Types:</p>
                    <div className="flex flex-wrap gap-1 mt-1">
                      {format.dataTypes.map((type, typeIndex) => (
                        <Badge key={typeIndex} variant="outline" className="text-xs">
                          {type}
                        </Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Export Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Export Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <p className="text-gray-600">
                Selected {selectedFormats.length} format(s) for export
              </p>
              <div className="flex gap-2">
                <Button 
                  variant="outline" 
                  onClick={() => setSelectedFormats([])}
                  disabled={selectedFormats.length === 0}
                >
                  Clear Selection
                </Button>
                <Button 
                  className="flex items-center gap-2"
                  disabled={selectedFormats.length === 0}
                >
                  <Download className="w-4 h-4" />
                  Export Selected ({selectedFormats.length})
                </Button>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-4">
              <Button variant="outline" className="flex items-center gap-2">
                <ExternalLink className="w-4 h-4" />
                API Access
              </Button>
              <Button variant="outline" className="flex items-center gap-2">
                <FileText className="w-4 h-4" />
                Documentation
              </Button>
              <Button variant="outline" className="flex items-center gap-2">
                <Network className="w-4 h-4" />
                Query Builder
              </Button>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg">
              <h4 className="font-medium text-blue-900 mb-2">Programmatic Access</h4>
              <p className="text-sm text-blue-800 mb-2">
                Access BioNexus data programmatically through our REST API
              </p>
              <code className="text-xs bg-blue-100 text-blue-900 p-2 rounded block">
                curl -X GET "http://localhost:8000/api/export/knowledge-graph" -H "Authorization: Bearer YOUR_TOKEN"
              </code>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}