'use client'

import React from 'react'
import { PipelineVisualization } from '@/components/pipeline/PipelineVisualization'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Zap, ArrowLeft } from 'lucide-react'
import Link from 'next/link'

export default function PipelinePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 hover:bg-white rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
              BioNexus Processing Pipeline
            </h1>
            <p className="text-gray-600">
              Complete data flow from PDF documents to knowledge discovery
            </p>
          </div>
        </div>

        {/* Pipeline Status Overview */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-blue-600" />
              System Status
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center p-3 bg-green-50 rounded-lg">
                <div className="text-2xl font-bold text-green-600">608</div>
                <div className="text-sm text-green-700">Documents Processed</div>
              </div>
              <div className="text-center p-3 bg-blue-50 rounded-lg">
                <div className="text-2xl font-bold text-blue-600">98.5%</div>
                <div className="text-sm text-blue-700">Pipeline Efficiency</div>
              </div>
              <div className="text-center p-3 bg-purple-50 rounded-lg">
                <div className="text-2xl font-bold text-purple-600">24.7K</div>
                <div className="text-sm text-purple-700">Entities Extracted</div>
              </div>
              <div className="text-center p-3 bg-orange-50 rounded-lg">
                <div className="text-2xl font-bold text-orange-600">1.8M</div>
                <div className="text-sm text-orange-700">Vector Embeddings</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Main Pipeline Visualization */}
        <PipelineVisualization />

        {/* Schema Compliance */}
        <Card>
          <CardHeader>
            <CardTitle>Schema Compliance Status</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-semibold mb-3">Input Processing</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">PDF Documents → Ingestion Pipeline</span>
                    <Badge variant="default">✓ Active</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Ingestion → OCR Engine</span>
                    <Badge variant="default">✓ Active</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Ingestion → ColPali Embeddings</span>
                    <Badge variant="secondary">⚠ Fallback Mode</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Ingestion → Biomedical NER</span>
                    <Badge variant="secondary">⚠ Fallback Mode</Badge>
                  </div>
                </div>
              </div>
              <div>
                <h4 className="font-semibold mb-3">Data Integration</h4>
                <div className="space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm">OCR → Neo4j Knowledge Graph</span>
                    <Badge variant="outline">⚠ Database Required</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Embeddings → Vector Database</span>
                    <Badge variant="default">✓ Mock Implementation</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">NER → Knowledge Graph</span>
                    <Badge variant="outline">⚠ Database Required</Badge>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm">Backend → Frontend Integration</span>
                    <Badge variant="default">✓ Active</Badge>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}