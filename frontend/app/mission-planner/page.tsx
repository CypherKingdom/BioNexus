'use client'

import React from 'react'
import { MissionPlanner } from '@/components/mission/MissionPlanner'
import { ArrowLeft, Rocket } from 'lucide-react'
import Link from 'next/link'

export default function MissionPlannerPage() {
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
              <Rocket className="w-8 h-8 text-blue-600" />
              <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                Mission Planning System
              </h1>
            </div>
            <p className="text-gray-600 mt-2">
              Research-driven mission planning powered by the complete BioNexus processing pipeline
            </p>
          </div>
        </div>

        {/* Mission Planner Component */}
        <MissionPlanner />
      </div>
    </div>
  )
}