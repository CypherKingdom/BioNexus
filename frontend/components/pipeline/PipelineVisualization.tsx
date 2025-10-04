'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { 
  FileText, 
  Zap, 
  Eye, 
  Brain, 
  Database, 
  Network, 
  Server, 
  Monitor, 
  ArrowRight,
  Play,
  CheckCircle,
  Clock,
  AlertTriangle
} from 'lucide-react'

interface PipelineStep {
  id: string
  name: string
  icon: React.ReactNode
  status: 'idle' | 'running' | 'completed' | 'error'
  description: string
  details: string[]
  color: string
}

export const PipelineVisualization: React.FC = () => {
  const [activeStep, setActiveStep] = useState<string>('neo4j')
  
  const pipelineSteps: PipelineStep[] = [
    {
      id: 'neo4j',
      name: 'Neo4j Knowledge Graph',
      icon: <Database className="w-6 h-6" />,
      status: 'completed',
      description: 'Pre-processed knowledge graph data',
      details: [
        '608 publications processed',
        'Biomedical entities extracted',
        'Research relationships mapped',
        'Multi-level entity connections'
      ],
      color: 'bg-[#0077b6] text-white'
    },
    {
      id: 'milvus',
      name: 'Milvus Vector Database',
      icon: <Brain className="w-6 h-6" />,
      status: 'completed',
      description: 'Pre-computed semantic embeddings',
      details: [
        'ColPali multimodal embeddings',
        'High-dimensional vector search',
        'Semantic similarity indexing',
        'Optimized query performance'
      ],
      color: 'bg-purple-600 text-white'
    },
    {
      id: 'ocr',
      name: 'OCR Engine',
      icon: <Eye className="w-6 h-6" />,
      status: 'completed',
      description: 'Optical Character Recognition processing',
      details: [
        'Tesseract OCR integration',
        'Image-to-text conversion',
        'Scientific notation handling',
        'Multi-language support'
      ],
      color: 'bg-blue-500 text-white'
    },
    {
      id: 'embeddings',
      name: 'ColPali Embeddings',
      icon: <Brain className="w-6 h-6" />,
      status: 'completed',
      description: 'Multimodal AI embeddings generation',
      details: [
        'Vision-language model processing',
        'Document-level embeddings',
        'Semantic understanding',
        'Cross-modal alignment'
      ],
      color: 'bg-purple-500 text-white'
    },
    {
      id: 'ner',
      name: 'Biomedical NER',
      icon: <Network className="w-6 h-6" />,
      status: 'completed',
      description: 'Named Entity Recognition for life sciences',
      details: [
        'Species identification',
        'Gene and protein extraction',
        'Experimental condition parsing',
        'Biological pathway recognition'
      ],
      color: 'bg-green-500 text-white'
    },
    {
      id: 'knowledge-graph',
      name: 'Neo4j Knowledge Graph',
      icon: <Database className="w-6 h-6" />,
      status: 'completed',
      description: 'Graph database for research relationships',
      details: [
        'Entity relationship modeling',
        'Research connection mapping',
        'Semantic querying',
        'Graph analytics'
      ],
      color: 'bg-[#0077b6] text-white'
    },
    {
      id: 'vector-db',
      name: 'Vector Database',
      icon: <Server className="w-6 h-6" />,
      status: 'completed',
      description: 'High-dimensional similarity search',
      details: [
        'FAISS vector indexing',
        'Semantic similarity search',
        'Fast retrieval optimization',
        'Scalable vector operations'
      ],
      color: 'bg-indigo-500 text-white'
    },
    {
      id: 'backend',
      name: 'FastAPI Backend',
      icon: <Server className="w-6 h-6" />,
      status: 'completed',
      description: 'RESTful API services',
      details: [
        'Search and retrieval endpoints',
        'Knowledge graph querying',
        'Mission planning algorithms',
        'Export and integration APIs'
      ],
      color: 'bg-[#00b4d8] text-white'
    },
    {
      id: 'frontend',
      name: 'Next.js Frontend',
      icon: <Monitor className="w-6 h-6" />,
      status: 'completed',
      description: 'Modern web application interface',
      details: [
        'Interactive search interface',
        'Knowledge graph visualization',
        'Mission planning dashboard',
        'Responsive design'
      ],
      color: 'bg-[#90e0ef] text-black'
    },
    {
      id: 'dashboard',
      name: 'BioNexus Dashboard',
      icon: <Monitor className="w-6 h-6" />,
      status: 'completed',
      description: 'Unified research exploration platform',
      details: [
        'Integrated search and discovery',
        'Research trend analysis',
        'Export capabilities',
        'Mission planning tools'
      ],
      color: 'bg-[#caf0f8] text-black'
    }
  ]

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-500" />
      case 'running':
        return <Clock className="w-5 h-5 text-yellow-500 animate-pulse" />
      case 'error':
        return <AlertTriangle className="w-5 h-5 text-red-500" />
      default:
        return <div className="w-5 h-5 rounded-full border-2 border-gray-300" />
    }
  }

  return (
    <div className="w-full space-y-6">
      {/* Pipeline Overview */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5 text-blue-600" />
            BioNexus Processing Pipeline
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
            {pipelineSteps.map((step, index) => (
              <div key={step.id} className="flex flex-col items-center">
                <div 
                  className={`w-16 h-16 rounded-lg ${step.color} flex items-center justify-center cursor-pointer hover:scale-105 transition-transform`}
                  onClick={() => setActiveStep(step.id)}
                >
                  {step.icon}
                </div>
                <div className="text-center mt-2">
                  <p className="text-sm font-medium text-gray-900 line-clamp-1">{step.name}</p>
                  <div className="flex items-center justify-center mt-1">
                    {getStatusIcon(step.status)}
                  </div>
                </div>
                {index < pipelineSteps.length - 1 && (
                  <ArrowRight className="w-4 h-4 text-gray-400 mt-2 hidden lg:block" />
                )}
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Detailed View */}
      <Tabs defaultValue={activeStep}>
        <TabsList className="grid w-full grid-cols-5 lg:grid-cols-10">
          {pipelineSteps.map((step) => (
            <TabsTrigger 
              key={step.id} 
              value={step.id} 
              className="text-xs"
              onClick={() => setActiveStep(step.id)}
            >
              <div className="flex items-center gap-1">
                {step.icon}
                <span className="hidden sm:inline">{step.name}</span>
              </div>
            </TabsTrigger>
          ))}
        </TabsList>

        {pipelineSteps.map((step) => (
          <TabsContent key={step.id} value={step.id} className="space-y-4">
            <Card>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className={`w-12 h-12 rounded-lg ${step.color} flex items-center justify-center`}>
                      {step.icon}
                    </div>
                    <div>
                      <CardTitle>{step.name}</CardTitle>
                      <p className="text-gray-600">{step.description}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {getStatusIcon(step.status)}
                    <Badge variant={
                      step.status === 'completed' ? 'default' :
                      step.status === 'running' ? 'secondary' :
                      step.status === 'error' ? 'destructive' : 'outline'
                    }>
                      {step.status}
                    </Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Key Features</h4>
                    <ul className="space-y-2">
                      {step.details.map((detail, index) => (
                        <li key={index} className="flex items-center gap-2 text-sm text-gray-600">
                          <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                          {detail}
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-900 mb-3">Integration Status</h4>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Service Health</span>
                        <Badge variant="default">Active</Badge>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Last Updated</span>
                        <span className="text-gray-600">2 minutes ago</span>
                      </div>
                      <div className="flex items-center justify-between text-sm">
                        <span>Processing Rate</span>
                        <span className="text-gray-600">98.5%</span>
                      </div>
                    </div>
                  </div>
                </div>

                {step.id === 'ingestion' && (
                  <div className="mt-6 p-4 bg-blue-50 rounded-lg">
                    <div className="flex items-center gap-2 mb-2">
                      <Play className="w-4 h-4 text-blue-600" />
                      <span className="font-medium text-blue-900">Currently Processing</span>
                    </div>
                    <p className="text-sm text-blue-800">
                      Processing document batch 15/20 - Analyzing molecular biology research papers
                    </p>
                    <div className="w-full bg-blue-200 rounded-full h-2 mt-2">
                      <div className="bg-blue-600 h-2 rounded-full" style={{ width: '75%' }}></div>
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        ))}
      </Tabs>

      {/* Mission Planner & Export Integration */}
      <div className="grid md:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Network className="w-5 h-5 text-purple-600" />
              Mission Planner Integration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Leverages the complete pipeline to provide research-based mission planning recommendations.
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Connected to Knowledge Graph</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>AI-powered recommendations</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Risk assessment algorithms</span>
              </div>
            </div>
            <Button className="w-full mt-4" variant="outline">
              Launch Mission Planner
            </Button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Database className="w-5 h-5 text-green-600" />
              Export System Integration
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-600 mb-4">
              Export processed data and insights in multiple formats for external analysis.
            </p>
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Knowledge graph exports</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Vector embeddings export</span>
              </div>
              <div className="flex items-center gap-2 text-sm">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Research summaries</span>
              </div>
            </div>
            <Button className="w-full mt-4" variant="outline">
              Access Export Tools
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}