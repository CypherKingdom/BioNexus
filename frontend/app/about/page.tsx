'use client'

import React from 'react'
import { RocketIcon, DatabaseIcon, BrainIcon, NetworkIcon, ServerIcon } from 'lucide-react'
import Link from 'next/link'

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <RocketIcon className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">About BioNexus</h1>
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link href="/" className="text-gray-600 hover:text-primary-700 transition-colors">Home</Link>
              <Link href="/search" className="text-gray-600 hover:text-primary-700 transition-colors">Search</Link>
              <Link href="/methodology" className="text-gray-600 hover:text-primary-700 transition-colors">Methodology</Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            AI-Powered NASA Bioscience Research Platform
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            BioNexus is a cutting-edge knowledge discovery platform that transforms NASA bioscience 
            publications into an interconnected, searchable, and analyzable research ecosystem.
          </p>
        </div>

        {/* Mission Statement */}
        <section className="mb-16">
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <h3 className="text-2xl font-bold text-gray-900 mb-6 text-center">Our Mission</h3>
            <p className="text-gray-700 text-lg leading-relaxed text-center max-w-3xl mx-auto">
              To accelerate scientific discovery by making NASA's vast bioscience research repository 
              instantly searchable, analyzable, and interconnected through advanced AI and knowledge 
              graph technologies.
            </p>
          </div>
        </section>

        {/* Key Features */}
        <section className="mb-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Platform Capabilities</h3>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center mr-4">
                  <BrainIcon className="w-6 h-6 text-blue-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900">AI-Powered Search</h4>
              </div>
              <p className="text-gray-600">
                Advanced semantic search using ColPali embeddings and natural language processing 
                to find relevant research across NASA's publication database.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center mr-4">
                  <NetworkIcon className="w-6 h-6 text-green-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900">Knowledge Graph</h4>
              </div>
              <p className="text-gray-600">
                Interactive visualization of research relationships, connecting publications, 
                entities, and concepts in a comprehensive knowledge network.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center mr-4">
                  <DatabaseIcon className="w-6 h-6 text-purple-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900">Cloud-Native Architecture</h4>
              </div>
              <p className="text-gray-600">
                Built on Neo4j Aura and Milvus Cloud for scalable, high-performance data 
                processing and retrieval with enterprise-grade reliability.
              </p>
            </div>

            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md transition-shadow">
              <div className="flex items-center mb-4">
                <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center mr-4">
                  <ServerIcon className="w-6 h-6 text-orange-600" />
                </div>
                <h4 className="text-lg font-semibold text-gray-900">Real-Time Processing</h4>
              </div>
              <p className="text-gray-600">
                Live data integration with OCR processing, biomedical entity recognition, 
                and continuous knowledge graph updates for the latest research insights.
              </p>
            </div>
          </div>
        </section>

        {/* Technology Stack */}
        <section className="mb-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Technology Stack</h3>
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <h4 className="font-semibold text-gray-900 mb-4">Backend</h4>
                <ul className="text-gray-600 space-y-2">
                  <li>FastAPI (Python)</li>
                  <li>Neo4j Aura (Graph DB)</li>
                  <li>Milvus Cloud (Vector DB)</li>
                  <li>OpenAI GPT-4</li>
                </ul>
              </div>
              <div className="text-center">
                <h4 className="font-semibold text-gray-900 mb-4">Frontend</h4>
                <ul className="text-gray-600 space-y-2">
                  <li>Next.js 14</li>
                  <li>React 18</li>
                  <li>TypeScript</li>
                  <li>Tailwind CSS</li>
                </ul>
              </div>
              <div className="text-center">
                <h4 className="font-semibold text-gray-900 mb-4">AI/ML</h4>
                <ul className="text-gray-600 space-y-2">
                  <li>ColPali Embeddings</li>
                  <li>Tesseract OCR</li>
                  <li>spaCy NER</li>
                  <li>Sentence Transformers</li>
                </ul>
              </div>
            </div>
          </div>
        </section>

        {/* Data Sources */}
        <section className="mb-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Data Sources</h3>
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <div className="text-center">
              <p className="text-gray-700 mb-6">
                BioNexus processes and analyzes NASA's comprehensive bioscience research database:
              </p>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-600 mb-2">NASA</div>
                  <div className="text-sm text-gray-600">Publications</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-600 mb-2">Life Sciences</div>
                  <div className="text-sm text-gray-600">Research</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-600 mb-2">Space Biology</div>
                  <div className="text-sm text-gray-600">Studies</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-primary-600 mb-2">Experimental</div>
                  <div className="text-sm text-gray-600">Data</div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Contact Information */}
        <section>
          <div className="bg-gradient-to-r from-primary-500 to-blue-600 rounded-xl p-8 text-white text-center">
            <h3 className="text-2xl font-bold mb-4">Ready to Explore?</h3>
            <p className="text-primary-100 mb-6">
              Start discovering connections in NASA's bioscience research today
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link 
                href="/search" 
                className="bg-white text-primary-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
              >
                Start Searching
              </Link>
              <Link 
                href="/graph" 
                className="border border-white text-white px-6 py-3 rounded-lg font-medium hover:bg-white hover:text-primary-600 transition-colors"
              >
                Explore Graph
              </Link>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}