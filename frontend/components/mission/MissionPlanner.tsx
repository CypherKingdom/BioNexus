'use client'

import React, { useState } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { 
  Rocket, 
  Target, 
  Brain, 
  AlertTriangle, 
  CheckCircle,
  Clock,
  TrendingUp,
  Database,
  Network,
  FileText,
  Eye,
  Zap
} from 'lucide-react'

interface MissionRequirement {
  category: string
  description: string
  importance: 'critical' | 'high' | 'medium' | 'low'
  status: 'met' | 'partial' | 'unmet'
}

interface ResearchInsight {
  title: string
  source: string
  relevance: number
  summary: string
  entityTypes: string[]
}

export const MissionPlanner: React.FC = () => {
  const [selectedMission, setSelectedMission] = useState<string>('mars-life')
  
  const missionTypes = [
    { id: 'mars-life', name: 'Mars Life Detection', icon: <Target className="w-5 h-5" /> },
    { id: 'moon-bio', name: 'Lunar Biosynthesis', icon: <Rocket className="w-5 h-5" /> },
    { id: 'iss-cell', name: 'ISS Cell Culture', icon: <Brain className="w-5 h-5" /> }
  ]

  const requirements: MissionRequirement[] = [
    {
      category: 'Organism Selection',
      description: 'Identify extremophile species suitable for Mars conditions',
      importance: 'critical',
      status: 'met'
    },
    {
      category: 'Environmental Tolerance',
      description: 'Understand radiation and temperature tolerance mechanisms',
      importance: 'critical',
      status: 'met'
    },
    {
      category: 'Life Detection Methods',
      description: 'Establish biomarker identification protocols',
      importance: 'high',
      status: 'partial'
    },
    {
      category: 'Sample Preservation',
      description: 'Develop protocols for sample collection and storage',
      importance: 'high',
      status: 'met'
    },
    {
      category: 'Contamination Control',
      description: 'Prevent forward and backward contamination',
      importance: 'medium',
      status: 'partial'
    }
  ]

  const insights: ResearchInsight[] = [
    {
      title: 'Tardigrade Extremophile Survival in Simulated Mars Environment',
      source: 'Johnson et al. (2023)',
      relevance: 95,
      summary: 'Tardigrades demonstrated remarkable survival rates in Mars-like conditions including low pressure and high radiation.',
      entityTypes: ['Tardigrade', 'Mars Environment', 'Radiation Tolerance']
    },
    {
      title: 'Biosignature Detection Using Machine Learning Approaches',
      source: 'Chen & Williams (2022)',
      relevance: 87,
      summary: 'Novel AI algorithms successfully identified microbial biosignatures in analog samples with 94% accuracy.',
      entityTypes: ['Biosignatures', 'Machine Learning', 'Microbial Detection']
    },
    {
      title: 'Metabolic Pathways in Extreme Cold Conditions',
      source: 'Rodriguez et al. (2023)',
      relevance: 82,
      summary: 'Study reveals key metabolic adaptations that enable life in cryogenic environments similar to Mars subsurface.',
      entityTypes: ['Metabolism', 'Extremophiles', 'Cold Adaptation']
    }
  ]

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'met':
        return 'bg-green-100 text-green-800'
      case 'partial':
        return 'bg-yellow-100 text-yellow-800'
      case 'unmet':
        return 'bg-red-100 text-red-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'critical':
        return 'bg-red-500 text-white'
      case 'high':
        return 'bg-orange-500 text-white'
      case 'medium':
        return 'bg-yellow-500 text-white'
      case 'low':
        return 'bg-blue-500 text-white'
      default:
        return 'bg-gray-500 text-white'
    }
  }

  return (
    <div className="space-y-6">
      {/* Mission Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Rocket className="w-5 h-5 text-blue-600" />
            Mission Planning Dashboard
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            {missionTypes.map((mission) => (
              <div
                key={mission.id}
                onClick={() => setSelectedMission(mission.id)}
                className={`p-4 rounded-lg border-2 cursor-pointer transition-colors ${
                  selectedMission === mission.id
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-blue-100 rounded-lg">
                    {mission.icon}
                  </div>
                  <div>
                    <h3 className="font-medium text-gray-900">{mission.name}</h3>
                    <p className="text-sm text-gray-600">Research-based planning</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Pipeline Integration Status */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Network className="w-5 h-5 text-purple-600" />
            Pipeline Integration Status
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center gap-3 p-3 bg-green-50 rounded-lg">
              <Database className="w-8 h-8 text-green-600" />
              <div>
                <p className="text-sm font-medium">Knowledge Graph</p>
                <p className="text-xs text-green-600">Connected</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-blue-50 rounded-lg">
              <Brain className="w-8 h-8 text-blue-600" />
              <div>
                <p className="text-sm font-medium">AI Embeddings</p>
                <p className="text-xs text-blue-600">Active</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-purple-50 rounded-lg">
              <Eye className="w-8 h-8 text-purple-600" />
              <div>
                <p className="text-sm font-medium">Entity Recognition</p>
                <p className="text-xs text-purple-600">Processing</p>
              </div>
            </div>
            <div className="flex items-center gap-3 p-3 bg-orange-50 rounded-lg">
              <FileText className="w-8 h-8 text-orange-600" />
              <div>
                <p className="text-sm font-medium">Research Base</p>
                <p className="text-xs text-orange-600">608 Papers</p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-2 gap-6">
        {/* Mission Requirements */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Target className="w-5 h-5 text-green-600" />
              Mission Requirements Analysis
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {requirements.map((req, index) => (
                <div key={index} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="font-medium text-gray-900">{req.category}</h4>
                    <div className="flex items-center gap-2">
                      <Badge className={getImportanceColor(req.importance)}>
                        {req.importance}
                      </Badge>
                      <Badge variant="outline" className={getStatusColor(req.status)}>
                        {req.status === 'met' ? (
                          <CheckCircle className="w-3 h-3 mr-1" />
                        ) : req.status === 'partial' ? (
                          <Clock className="w-3 h-3 mr-1" />
                        ) : (
                          <AlertTriangle className="w-3 h-3 mr-1" />
                        )}
                        {req.status}
                      </Badge>
                    </div>
                  </div>
                  <p className="text-sm text-gray-600">{req.description}</p>
                </div>
              ))}
            </div>

            <div className="mt-6 p-4 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-4 h-4 text-blue-600" />
                <span className="font-medium">Readiness Score</span>
              </div>
              <div className="flex items-center gap-3">
                <div className="flex-1 bg-gray-200 rounded-full h-3">
                  <div className="bg-green-500 h-3 rounded-full" style={{ width: '78%' }}></div>
                </div>
                <span className="text-sm font-medium text-gray-900">78%</span>
              </div>
              <p className="text-xs text-gray-600 mt-1">Based on research coverage and requirement fulfillment</p>
            </div>
          </CardContent>
        </Card>

        {/* Research Insights */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-purple-600" />
              Relevant Research Insights
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {insights.map((insight, index) => (
                <div key={index} className="border rounded-lg p-4 hover:border-blue-200 transition-colors">
                  <div className="flex items-start justify-between mb-2">
                    <h4 className="font-medium text-gray-900 text-sm line-clamp-1">{insight.title}</h4>
                    <Badge variant="outline" className="text-xs">
                      {insight.relevance}% match
                    </Badge>
                  </div>
                  <p className="text-xs text-gray-600 mb-2">{insight.source}</p>
                  <p className="text-sm text-gray-700 mb-3">{insight.summary}</p>
                  <div className="flex flex-wrap gap-1">
                    {insight.entityTypes.map((entity, entityIndex) => (
                      <Badge key={entityIndex} variant="secondary" className="text-xs">
                        {entity}
                      </Badge>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <Button className="w-full mt-4" variant="outline">
              <Zap className="w-4 h-4 mr-2" />
              Generate Mission Report
            </Button>
          </CardContent>
        </Card>
      </div>

      {/* Action Panel */}
      <Card>
        <CardHeader>
          <CardTitle>Mission Planning Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid md:grid-cols-3 gap-4">
            <Button className="flex items-center gap-2" size="lg">
              <FileText className="w-4 h-4" />
              Export Mission Brief
            </Button>
            <Button variant="outline" className="flex items-center gap-2" size="lg">
              <Network className="w-4 h-4" />
              Explore Knowledge Graph
            </Button>
            <Button variant="outline" className="flex items-center gap-2" size="lg">
              <TrendingUp className="w-4 h-4" />
              Risk Assessment
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}