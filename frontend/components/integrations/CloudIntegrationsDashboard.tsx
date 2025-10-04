import React, { useState, useEffect } from 'react'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { 
  Cloud, 
  Globe, 
  Users, 
  BarChart3, 
  Zap, 
  MapPin,
  Brain,
  Lightbulb
} from 'lucide-react'

interface CloudIntegrationsProps {
  researchId?: string
}

export const CloudIntegrationsDashboard: React.FC<CloudIntegrationsProps> = ({ 
  researchId 
}) => {
  const [integrationStatus, setIntegrationStatus] = useState({
    meteomatics: { status: 'connected', lastSync: '2024-01-01T12:00:00Z' },
    azure: { status: 'connected', lastSync: '2024-01-01T12:30:00Z' },
    miro: { status: 'connected', lastSync: '2024-01-01T13:00:00Z' },
    googleCloud: { status: 'connected', lastSync: '2024-01-01T13:30:00Z' }
  })
  
  const [environmentalData, setEnvironmentalData] = useState(null)
  const [aiInsights, setAiInsights] = useState(null)
  const [collaborationStats, setCollaborationStats] = useState(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (researchId) {
      fetchMultiPlatformInsights()
    }
  }, [researchId])

  const fetchMultiPlatformInsights = async () => {
    setLoading(true)
    try {
      const response = await fetch(
        `/api/integrations/insights/multi-platform/${researchId}?include_environment=true&include_ai_analysis=true`
      )
      const data = await response.json()
      
      setEnvironmentalData(data.platforms?.meteomatics)
      setAiInsights(data.platforms?.azure_ai)
      
    } catch (error) {
      console.error('Failed to fetch multi-platform insights:', error)
    } finally {
      setLoading(false)
    }
  }

  const createMiroWorkspace = async () => {
    if (!researchId) return
    
    try {
      const response = await fetch('/api/integrations/collaboration/create-workspace', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          research_id: researchId,
          title: 'BioNexus Research Collaboration',
          research_area: 'Biomedical Sciences',
          collaborators: ['team@bionexus.space'],
          include_templates: true
        })
      })
      
      const workspace = await response.json()
      
      if (workspace.workspace_url) {
        window.open(workspace.workspace_url, '_blank')
      }
      
    } catch (error) {
      console.error('Failed to create Miro workspace:', error)
    }
  }

  const analyzeWithAzureAI = async (text: string) => {
    try {
      const response = await fetch('/api/integrations/ai/analyze-text', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: text,
          analysis_types: ['entities', 'sentiment', 'key_phrases']
        })
      })
      
      const analysis = await response.json()
      setAiInsights(analysis)
      
    } catch (error) {
      console.error('Failed to analyze with Azure AI:', error)
    }
  }

  return (
    <div className="w-full space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-3xl font-bold">Cloud Integrations</h2>
          <p className="text-muted-foreground">
            Leverage external platforms to enhance your research
          </p>
        </div>
        <div className="flex items-center space-x-2">
          <Badge variant="outline" className="text-green-600 border-green-600">
            <Cloud className="w-4 h-4 mr-1" />
            All Systems Online
          </Badge>
        </div>
      </div>

      {/* Integration Status Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Meteomatics</CardTitle>
            <MapPin className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-blue-600">Weather API</div>
            <p className="text-xs text-muted-foreground">
              Environmental context analysis
            </p>
            <Badge 
              variant={integrationStatus.meteomatics.status === 'connected' ? 'default' : 'destructive'}
              className="mt-2"
            >
              {integrationStatus.meteomatics.status}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Azure AI</CardTitle>
            <Brain className="h-4 w-4 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-purple-600">Cognitive Services</div>
            <p className="text-xs text-muted-foreground">
              Enhanced text & image analysis
            </p>
            <Badge 
              variant={integrationStatus.azure.status === 'connected' ? 'default' : 'destructive'}
              className="mt-2"
            >
              {integrationStatus.azure.status}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Miro</CardTitle>
            <Users className="h-4 w-4 text-orange-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-orange-600">Collaboration</div>
            <p className="text-xs text-muted-foreground">
              Team whiteboards & brainstorming
            </p>
            <Badge 
              variant={integrationStatus.miro.status === 'connected' ? 'default' : 'destructive'}
              className="mt-2"
            >
              {integrationStatus.miro.status}
            </Badge>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Google Cloud</CardTitle>
            <Globe className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Infrastructure</div>
            <p className="text-xs text-muted-foreground">
              Scalable cloud platform
            </p>
            <Badge 
              variant={integrationStatus.googleCloud.status === 'connected' ? 'default' : 'destructive'}
              className="mt-2"
            >
              {integrationStatus.googleCloud.status}
            </Badge>
          </CardContent>
        </Card>
      </div>

      {/* Main Integration Tabs */}
      <Tabs defaultValue="environmental" className="w-full">
        <TabsList className="grid w-full grid-cols-4">
          <TabsTrigger value="environmental">Environmental</TabsTrigger>
          <TabsTrigger value="ai-analysis">AI Analysis</TabsTrigger>
          <TabsTrigger value="collaboration">Collaboration</TabsTrigger>
          <TabsTrigger value="analytics">Analytics</TabsTrigger>
        </TabsList>

        {/* Environmental Context Tab */}
        <TabsContent value="environmental" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <MapPin className="mr-2 h-5 w-5 text-blue-500" />
                Environmental Context Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {environmentalData ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="p-4 bg-blue-50 rounded-lg">
                      <h4 className="font-semibold text-blue-900">Solar Radiation</h4>
                      <p className="text-2xl font-bold text-blue-600">
                        {environmentalData.correlations?.solar_radiation_impact || 'Low'}
                      </p>
                      <p className="text-sm text-blue-700">Impact Level</p>
                    </div>
                    <div className="p-4 bg-purple-50 rounded-lg">
                      <h4 className="font-semibold text-purple-900">Cosmic Radiation</h4>
                      <p className="text-2xl font-bold text-purple-600">
                        {environmentalData.correlations?.cosmic_ray_correlation || 'Medium'}
                      </p>
                      <p className="text-sm text-purple-700">Correlation</p>
                    </div>
                    <div className="p-4 bg-green-50 rounded-lg">
                      <h4 className="font-semibold text-green-900">Geomagnetic Activity</h4>
                      <p className="text-2xl font-bold text-green-600">
                        {environmentalData.correlations?.geomagnetic_influence || 'Low'}
                      </p>
                      <p className="text-sm text-green-700">Influence</p>
                    </div>
                  </div>
                  
                  {environmentalData.insights && (
                    <div className="space-y-2">
                      <h4 className="font-semibold">Environmental Insights</h4>
                      {environmentalData.insights.map((insight: string, index: number) => (
                        <Alert key={index}>
                          <Lightbulb className="h-4 w-4" />
                          <AlertDescription>{insight}</AlertDescription>
                        </Alert>
                      ))}
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    No environmental data available. Select a research project to analyze environmental correlations.
                  </p>
                  <Button onClick={fetchMultiPlatformInsights} disabled={!researchId || loading}>
                    <MapPin className="mr-2 h-4 w-4" />
                    {loading ? 'Analyzing...' : 'Analyze Environmental Context'}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* AI Analysis Tab */}
        <TabsContent value="ai-analysis" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Brain className="mr-2 h-5 w-5 text-purple-500" />
                Azure AI Enhanced Analysis
              </CardTitle>
            </CardHeader>
            <CardContent>
              {aiInsights ? (
                <div className="space-y-4">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="font-semibold mb-2">Entity Recognition</h4>
                      <div className="space-y-2">
                        <div className="flex justify-between text-sm">
                          <span>Total Entities:</span>
                          <Badge>{aiInsights.entity_count || 0}</Badge>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>High Confidence:</span>
                          <Badge variant="outline">
                            {aiInsights.confidence_scores?.high_confidence_count || 0}
                          </Badge>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Validation Status:</span>
                          <Badge variant={aiInsights.validation_status === 'cross_validated' ? 'default' : 'secondary'}>
                            {aiInsights.validation_status || 'Unknown'}
                          </Badge>
                        </div>
                      </div>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold mb-2">Confidence Distribution</h4>
                      <div className="space-y-2">
                        {aiInsights.confidence_scores && (
                          <>
                            <div className="flex items-center justify-between">
                              <span className="text-sm">Average:</span>
                              <span className="font-mono">
                                {(aiInsights.confidence_scores.mean * 100).toFixed(1)}%
                              </span>
                            </div>
                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-blue-600 h-2 rounded-full" 
                                style={{ 
                                  width: `${(aiInsights.confidence_scores.mean * 100)}%` 
                                }}
                              ></div>
                            </div>
                          </>
                        )}
                      </div>
                    </div>
                  </div>

                  {aiInsights.entities && aiInsights.entities.length > 0 && (
                    <div>
                      <h4 className="font-semibold mb-2">Top Entities</h4>
                      <div className="flex flex-wrap gap-2">
                        {aiInsights.entities.slice(0, 20).map((entity: any, index: number) => (
                          <Badge 
                            key={index} 
                            variant="outline"
                            className="text-xs"
                          >
                            {entity.text} ({(entity.confidence * 100).toFixed(0)}%)
                          </Badge>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="text-center py-8">
                  <p className="text-muted-foreground mb-4">
                    No AI analysis available. Perform enhanced text analysis using Azure Cognitive Services.
                  </p>
                  <Button onClick={() => analyzeWithAzureAI("Sample research text")} disabled={loading}>
                    <Brain className="mr-2 h-4 w-4" />
                    {loading ? 'Analyzing...' : 'Run AI Analysis'}
                  </Button>
                </div>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        {/* Collaboration Tab */}
        <TabsContent value="collaboration" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Users className="mr-2 h-5 w-5 text-orange-500" />
                Miro Collaboration Workspace
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="p-4 bg-orange-50 rounded-lg">
                    <h4 className="font-semibold text-orange-900">Active Workspaces</h4>
                    <p className="text-2xl font-bold text-orange-600">
                      {collaborationStats?.active_workspaces || 0}
                    </p>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-900">Team Members</h4>
                    <p className="text-2xl font-bold text-blue-600">
                      {collaborationStats?.team_members || 0}
                    </p>
                  </div>
                </div>

                <div className="space-y-3">
                  <Button onClick={createMiroWorkspace} className="w-full" disabled={!researchId}>
                    <Users className="mr-2 h-4 w-4" />
                    Create Research Collaboration Workspace
                  </Button>
                  
                  <Alert>
                    <Lightbulb className="h-4 w-4" />
                    <AlertDescription>
                      Miro workspaces include research templates, knowledge graph visualization, 
                      discussion areas, and real-time collaboration tools.
                    </AlertDescription>
                  </Alert>
                </div>

                <div className="border-t pt-4">
                  <h4 className="font-semibold mb-2">Collaboration Features</h4>
                  <ul className="space-y-1 text-sm text-muted-foreground">
                    <li>• Real-time collaborative whiteboards</li>
                    <li>• Research methodology templates</li>
                    <li>• Knowledge graph visualization</li>
                    <li>• Team discussion areas</li>
                    <li>• Automatic BioNexus sync</li>
                  </ul>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <BarChart3 className="mr-2 h-5 w-5 text-green-500" />
                Cloud Analytics & Insights
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="p-4 bg-green-50 rounded-lg">
                    <h4 className="font-semibold text-green-900">Platform Usage</h4>
                    <p className="text-2xl font-bold text-green-600">94%</p>
                    <p className="text-sm text-green-700">Uptime</p>
                  </div>
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <h4 className="font-semibold text-blue-900">API Calls Today</h4>
                    <p className="text-2xl font-bold text-blue-600">1,247</p>
                    <p className="text-sm text-blue-700">Cross-platform</p>
                  </div>
                  <div className="p-4 bg-purple-50 rounded-lg">
                    <h4 className="font-semibold text-purple-900">Cost Efficiency</h4>
                    <p className="text-2xl font-bold text-purple-600">$0.12</p>
                    <p className="text-sm text-purple-700">Per analysis</p>
                  </div>
                </div>

                <Alert>
                  <BarChart3 className="h-4 w-4" />
                  <AlertDescription>
                    Cloud integrations are operating efficiently. All platforms are responding 
                    within acceptable latency thresholds.
                  </AlertDescription>
                </Alert>

                <div>
                  <h4 className="font-semibold mb-2">Recent Integration Activity</h4>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span>Environmental analysis completed</span>
                      <Badge variant="outline">2 min ago</Badge>
                    </div>
                    <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span>AI entity extraction finished</span>
                      <Badge variant="outline">5 min ago</Badge>
                    </div>
                    <div className="flex justify-between items-center p-2 bg-gray-50 rounded">
                      <span>Miro workspace synced</span>
                      <Badge variant="outline">12 min ago</Badge>
                    </div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}