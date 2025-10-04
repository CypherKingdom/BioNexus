'use client'

import { useState } from 'react'
import { SearchIcon, BookOpenIcon, NetworkIcon, TrendingUpIcon, Zap, Database, Brain } from 'lucide-react'
import Link from 'next/link'
import { SearchBar } from '@/components/search/SearchBar'
import { StatsCards } from '@/components/dashboard/StatsCards'
import { RecentActivity } from '@/components/dashboard/RecentActivity'
import { TopicTrends } from '@/components/dashboard/TopicTrends'
import { PipelineVisualization } from '@/components/pipeline/PipelineVisualization'

export default function HomePage() {
  const [searchQuery, setSearchQuery] = useState('')

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                  <NetworkIcon className="w-5 h-5 text-white" />
                </div>
                <h1 className="text-2xl font-bold text-gradient">BioNexus</h1>
              </div>
            </div>
            
            <nav className="hidden md:flex items-center space-x-8">
              <Link href="/" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Dashboard
              </Link>
              <Link href="/search" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Search
              </Link>
              <Link href="/graph" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Knowledge Graph
              </Link>
              <Link href="/mission-planner" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Mission Planner
              </Link>
              <Link href="/export" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Export
              </Link>
              <Link href="/pipeline" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Pipeline
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="relative py-20 overflow-hidden">
        <div className="absolute inset-0 gradient-bg opacity-10"></div>
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6">
            NASA Bioscience
            <span className="text-gradient block">Intelligence Pipeline</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Complete AI-powered processing pipeline from PDF documents to mission planning. 
            OCR extraction, multimodal embeddings, biomedical NER, and knowledge graph integration.
          </p>
          
          {/* Main Search */}
          <div className="max-w-2xl mx-auto mb-12">
            <SearchBar
              value={searchQuery}
              onChange={setSearchQuery}
              placeholder="Search bioscience research, organisms, experiments..."
              size="large"
              onSearch={() => {
                if (searchQuery) {
                  window.location.href = `/search?q=${encodeURIComponent(searchQuery)}`
                }
              }}
            />
          </div>
          
          {/* Quick Action Cards */}
          <div className="grid md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <Link href="/search" className="card-hover group">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                  <SearchIcon className="w-6 h-6 text-primary-700" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900">Semantic Search</h3>
                  <p className="text-gray-600 text-sm">Find relevant research using natural language</p>
                </div>
              </div>
            </Link>
            
            <Link href="/graph" className="card-hover group">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                  <NetworkIcon className="w-6 h-6 text-primary-700" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900">Knowledge Graph</h3>
                  <p className="text-gray-600 text-sm">Explore connections between research concepts</p>
                </div>
              </div>
            </Link>
            
            <Link href="/mission-planner" className="card-hover group">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-colors">
                  <TrendingUpIcon className="w-6 h-6 text-primary-700" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900">Mission Planning</h3>
                  <p className="text-gray-600 text-sm">Get research-based mission recommendations</p>
                </div>
              </div>
            </Link>
          </div>
        </div>
      </section>

      {/* Pipeline Visualization */}
      <section className="py-12 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h3 className="text-3xl font-bold text-gray-900 mb-4">
              Processing Pipeline Architecture
            </h3>
            <p className="text-lg text-gray-600 max-w-3xl mx-auto">
              From PDF documents to knowledge discovery - see how BioNexus transforms 
              NASA research through advanced AI and data processing technologies.
            </p>
          </div>
          <PipelineVisualization />
        </div>
      </section>

      {/* Dashboard Content */}
      <section className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Statistics */}
          <StatsCards />
          
          <div className="grid lg:grid-cols-2 gap-8 mt-12">
            {/* Recent Activity */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Recent Research Highlights</h3>
              <RecentActivity />
            </div>
            
            {/* Topic Trends */}
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Research Topic Trends</h3>
              <TopicTrends />
            </div>
          </div>
          
          {/* Featured Publications */}
          <div className="card mt-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Featured Publications</h3>
              <Link href="/search" className="btn-outline text-sm">
                View All
              </Link>
            </div>
            
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {/* Placeholder for featured publications */}
              {[1, 2, 3].map((i) => (
                <div key={i} className="border border-gray-200 rounded-lg p-4 hover:border-primary-200 transition-colors">
                  <div className="flex items-start space-x-3">
                    <BookOpenIcon className="w-5 h-5 text-primary-500 mt-1 flex-shrink-0" />
                    <div>
                      <h4 className="font-medium text-gray-900 line-clamp-2">
                        Effects of Microgravity on Cellular Function and Gene Expression
                      </h4>
                      <p className="text-sm text-gray-600 mt-1">
                        Johnson, M. et al. • 2023
                      </p>
                      <div className="flex items-center space-x-2 mt-2">
                        <span className="entity-organism">Human</span>
                        <span className="entity-endpoint">Gene Expression</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>
      
      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-3 gap-8">
            <div>
              <div className="flex items-center space-x-2 mb-4">
                <div className="w-6 h-6 bg-primary-500 rounded flex items-center justify-center">
                  <NetworkIcon className="w-4 h-4 text-white" />
                </div>
                <span className="font-bold">BioNexus</span>
              </div>
              <p className="text-gray-400 text-sm">
                AI-powered knowledge graph platform for NASA bioscience research exploration and mission planning.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link href="/search" className="hover:text-white transition-colors">Search</Link></li>
                <li><Link href="/graph" className="hover:text-white transition-colors">Knowledge Graph</Link></li>
                <li><Link href="/mission-planner" className="hover:text-white transition-colors">Mission Planner</Link></li>
                <li><Link href="/api/docs" className="hover:text-white transition-colors">API Documentation</Link></li>
              </ul>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Resources</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link href="/about" className="hover:text-white transition-colors">About</Link></li>
                <li><Link href="/methodology" className="hover:text-white transition-colors">Methodology</Link></li>
                <li><Link href="/export" className="hover:text-white transition-colors">Export Data</Link></li>
                <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-sm text-gray-400">
            <p>&copy; 2024 BioNexus. Built for NASA bioscience research exploration.</p>
          </div>
        </div>
      </footer>
    </div>
  )
}