'use client'

import React from 'react'
import { CloudIntegrationsDashboard } from '@/components/integrations/CloudIntegrationsDashboard'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Cloud, Globe, Zap } from 'lucide-react'

export default function CloudIntegrationsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="text-center space-y-4">
          <div className="flex items-center justify-center gap-3">
            <Cloud className="h-8 w-8 text-blue-600" />
            <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              BioNexus Cloud Integrations
            </h1>
          </div>
          <p className="text-lg text-gray-600 max-w-3xl mx-auto">
            Comprehensive cloud platform integration dashboard showcasing external service connections 
            including weather data, AI analysis, collaboration tools, and cloud infrastructure.
          </p>
        </div>

        {/* Status Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Globe className="h-5 w-5" />
              Integration Status Overview
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="flex items-center gap-3">
                <Zap className="h-8 w-8 text-green-500" />
                <div>
                  <p className="font-semibold">Meteomatics Weather</p>
                  <Badge variant="default" className="bg-green-100 text-green-800">Connected</Badge>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Zap className="h-8 w-8 text-blue-500" />
                <div>
                  <p className="font-semibold">Azure AI Services</p>
                  <Badge variant="default" className="bg-blue-100 text-blue-800">Connected</Badge>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Zap className="h-8 w-8 text-purple-500" />
                <div>
                  <p className="font-semibold">Miro Collaboration</p>
                  <Badge variant="default" className="bg-purple-100 text-purple-800">Connected</Badge>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <Cloud className="h-8 w-8 text-orange-500" />
                <div>
                  <p className="font-semibold">Google Cloud Platform</p>
                  <Badge variant="default" className="bg-orange-100 text-orange-800">Active</Badge>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Dashboard */}
        <CloudIntegrationsDashboard researchId="demo-research-001" />

        {/* Deployment Information */}
        <Card>
          <CardHeader>
            <CardTitle>Cloud Deployment Resources</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold text-lg mb-2">Infrastructure</h4>
                <ul className="space-y-2 text-sm">
                  <li>✅ Terraform Infrastructure as Code</li>
                  <li>✅ Google Cloud Run Services</li>
                  <li>✅ BigQuery Data Warehouse</li>
                  <li>✅ Cloud Storage & CDN</li>
                  <li>✅ Secret Manager Configuration</li>
                </ul>
              </div>
              <div>
                <h4 className="font-semibold text-lg mb-2">External Integrations</h4>
                <ul className="space-y-2 text-sm">
                  <li>🌤️ Meteomatics Weather API</li>
                  <li>🧠 Azure Cognitive Services</li>
                  <li>📋 Miro Collaboration Platform</li>
                  <li>🌐 GoDaddy Domain Management</li>
                  <li>📊 Comprehensive Analytics</li>
                </ul>
              </div>
            </div>
            <div className="mt-6 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800">
                <strong>Ready for Deployment:</strong> All components are configured and ready for cloud deployment. 
                Use the deployment scripts in the project root to initialize the infrastructure.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}