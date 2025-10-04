'use client'

import React from 'react'
import { ExportSystem } from '@/components/export/ExportSystem'
import { ArrowLeft, Download } from 'lucide-react'
import Link from 'next/link'

export default function ExportPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center gap-4">
          <Link href="/" className="p-2 hover:bg-white rounded-lg transition-colors">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <div className="flex items-center gap-3">
              <Download className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Data Export System
              </h1>
            </div>
            <p className="text-gray-600 mt-2">
              Export processed research data from the BioNexus pipeline in multiple formats
            </p>
          </div>
        </div>

        {/* Export System Component */}
        <ExportSystem />
      </div>
    </div>
  )
}