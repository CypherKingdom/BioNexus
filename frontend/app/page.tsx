'use client'

import { useState } from 'react'
import { SearchIcon, BookOpenIcon, NetworkIcon, FileText, Zap, Database, Brain } from 'lucide-react'
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
              <Link href="/knowledge-graph" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Knowledge Graph
              </Link>
              <Link href="/search" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Search
              </Link>
              <Link href="/about" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                About
              </Link>
              <Link href="/methodology" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Methodology
              </Link>
              <Link href="/contact" className="text-gray-600 hover:text-primary-700 font-medium transition-colors">
                Contact
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
            <span className="text-gradient block">Knowledge Graph</span>
          </h2>
          <p className="text-xl text-gray-600 mb-8 max-w-3xl mx-auto">
            Explore connections in NASA bioscience research through an interactive knowledge graph. 
            Search 4,359 nodes of real data including publications, entities, and relationships.
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
                  window.location.href = `/knowledge-graph`
                }
              }}
            />
          </div>
          
          {/* Quick Action Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-4xl mx-auto">
            <Link href="/search" className="card-hover group hover-lift">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-all duration-300 group-hover:scale-110">
                  <SearchIcon className="w-6 h-6 text-primary-700 group-hover:text-primary-800" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">Search Knowledge Graph</h3>
                  <p className="text-gray-600 text-sm">Find entities and connections in real data</p>
                </div>
              </div>
            </Link>
            
            <Link href="/knowledge-graph" className="card-hover group hover-lift">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-all duration-300 group-hover:scale-110">
                  <NetworkIcon className="w-6 h-6 text-primary-700 group-hover:text-primary-800" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">Interactive Graph</h3>
                  <p className="text-gray-600 text-sm">Visualize real research connections</p>
                </div>
              </div>
            </Link>
            
            <Link href="/search" className="card-hover group hover-lift">
              <div className="flex items-center space-x-4">
                <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center group-hover:bg-primary-200 transition-all duration-300 group-hover:scale-110">
                  <FileText className="w-6 h-6 text-primary-700 group-hover:text-primary-800" />
                </div>
                <div className="text-left">
                  <h3 className="font-semibold text-gray-900 group-hover:text-primary-700 transition-colors">Document Search</h3>
                  <p className="text-gray-600 text-sm">Search through publication content</p>
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
          
          {/* Real Publications - Show only if data available */}
          <div className="card mt-8">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-lg font-semibold text-gray-900">Recent Publications</h3>
              <Link href="/search" className="btn-outline text-sm">
                Search All
              </Link>
            </div>
            
            <div className="text-center py-8 text-gray-500">
              <BookOpenIcon className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p className="text-lg font-medium mb-2">Real Publication Data</p>
              <p className="text-sm">
                Use the search functionality to explore actual NASA publications in the database
              </p>
              <Link href="/search" className="btn-primary mt-4 inline-flex items-center">
                <SearchIcon className="w-4 h-4 mr-2" />
                Start Searching
              </Link>
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
                AI-powered knowledge graph platform for NASA bioscience research exploration and analysis.
              </p>
            </div>
            
            <div>
              <h4 className="font-semibold mb-4">Platform</h4>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link href="/search" className="hover:text-white transition-colors">Search</Link></li>
                <li><Link href="/graph" className="hover:text-white transition-colors">Knowledge Graph</Link></li>

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