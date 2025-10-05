'use client'

import React from 'react'
import { BookOpenIcon, CpuIcon, DatabaseIcon, NetworkIcon, ZapIcon, EyeIcon } from 'lucide-react'
import Link from 'next/link'

export default function MethodologyPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <BookOpenIcon className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">Methodology</h1>
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link href="/" className="text-gray-600 hover:text-primary-700 transition-colors">Home</Link>
              <Link href="/about" className="text-gray-600 hover:text-primary-700 transition-colors">About</Link>
              <Link href="/pipeline" className="text-gray-600 hover:text-primary-700 transition-colors">Pipeline</Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            BioNexus Processing Methodology
          </h2>
          <p className="text-xl text-gray-600 max-w-4xl mx-auto">
            A comprehensive overview of our AI-powered pipeline for transforming NASA bioscience 
            publications into a searchable knowledge graph with semantic understanding.
          </p>
        </div>

        {/* Processing Pipeline */}
        <section className="mb-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Processing Pipeline</h3>
          <div className="space-y-8">
            {/* Step 1: Document Ingestion */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <BookOpenIcon className="w-6 h-6 text-blue-600" />
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">1. Document Ingestion</h4>
                  <p className="text-gray-700 mb-4">
                    NASA bioscience publications are ingested in PDF format and processed through 
                    our document parsing pipeline to extract text, metadata, and structural information.
                  </p>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Input Sources:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• NASA Technical Publications</li>
                        <li>• Life Sciences Research Papers</li>
                        <li>• Space Biology Studies</li>
                        <li>• Experimental Reports</li>
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Metadata Extracted:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Title and Authors</li>
                        <li>• Publication Date</li>
                        <li>• Abstract and Keywords</li>
                        <li>• Document Structure</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 2: OCR Processing */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <EyeIcon className="w-6 h-6 text-green-600" />
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">2. OCR Text Extraction</h4>
                  <p className="text-gray-700 mb-4">
                    Tesseract OCR engine processes document images to extract machine-readable text, 
                    handling scientific notation, tables, and complex layouts common in research papers.
                  </p>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">OCR Capabilities:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Multi-language text recognition</li>
                        <li>• Scientific notation handling</li>
                        <li>• Table structure preservation</li>
                        <li>• Image caption extraction</li>
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Post-Processing:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Text cleaning and normalization</li>
                        <li>• Confidence scoring</li>
                        <li>• Error correction</li>
                        <li>• Format standardization</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 3: AI Embeddings */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <CpuIcon className="w-6 h-6 text-purple-600" />
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">3. ColPali Multimodal Embeddings</h4>
                  <p className="text-gray-700 mb-4">
                    Advanced vision-language model creates high-dimensional vector representations 
                    that capture both textual content and visual document layout for semantic search.
                  </p>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Embedding Features:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• 384-dimensional vectors</li>
                        <li>• Cross-modal understanding</li>
                        <li>• Context-aware encoding</li>
                        <li>• Semantic similarity capture</li>
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Applications:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Semantic document search</li>
                        <li>• Similar research discovery</li>
                        <li>• Concept clustering</li>
                        <li>• Relevance ranking</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 4: Entity Recognition */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-orange-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <ZapIcon className="w-6 h-6 text-orange-600" />
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">4. Biomedical Named Entity Recognition</h4>
                  <p className="text-gray-700 mb-4">
                    Specialized spaCy models identify and classify biological entities, experimental 
                    conditions, and scientific concepts within the extracted text.
                  </p>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Entity Types:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Organisms and Species</li>
                        <li>• Genes and Proteins</li>
                        <li>• Chemical Compounds</li>
                        <li>• Experimental Conditions</li>
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Recognition Features:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Context-aware classification</li>
                        <li>• Confidence scoring</li>
                        <li>• Relationship extraction</li>
                        <li>• Domain-specific training</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 5: Knowledge Graph Construction */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-indigo-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <NetworkIcon className="w-6 h-6 text-indigo-600" />
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">5. Neo4j Knowledge Graph</h4>
                  <p className="text-gray-700 mb-4">
                    Extracted entities and relationships are structured into a graph database, 
                    creating interconnected networks of research knowledge for exploration and analysis.
                  </p>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Graph Structure:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Publication nodes</li>
                        <li>• Entity relationship edges</li>
                        <li>• Hierarchical organization</li>
                        <li>• Cross-reference connections</li>
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Query Capabilities:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Cypher query language</li>
                        <li>• Path finding algorithms</li>
                        <li>• Centrality analysis</li>
                        <li>• Subgraph extraction</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Step 6: Vector Database */}
            <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
              <div className="flex items-start gap-6">
                <div className="w-12 h-12 bg-cyan-100 rounded-lg flex items-center justify-center flex-shrink-0">
                  <DatabaseIcon className="w-6 h-6 text-cyan-600" />
                </div>
                <div className="flex-1">
                  <h4 className="text-xl font-semibold text-gray-900 mb-4">6. Milvus Vector Storage</h4>
                  <p className="text-gray-700 mb-4">
                    High-dimensional embeddings are stored in Milvus Cloud for fast similarity search 
                    and retrieval, enabling semantic queries across the entire research corpus.
                  </p>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Storage Features:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Billion-scale vector indexing</li>
                        <li>• Millisecond query response</li>
                        <li>• Distributed architecture</li>
                        <li>• ACID transactions</li>
                      </ul>
                    </div>
                    <div>
                      <h5 className="font-medium text-gray-900 mb-2">Search Algorithms:</h5>
                      <ul className="text-gray-600 text-sm space-y-1">
                        <li>• Approximate nearest neighbor</li>
                        <li>• Cosine similarity ranking</li>
                        <li>• Multi-vector queries</li>
                        <li>• Filtered search</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Technical Specifications */}
        <section className="mb-16">
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Technical Specifications</h3>
          <div className="grid md:grid-cols-3 gap-8">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">Performance Metrics</h4>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Sub-second semantic search</li>
                <li>• 99.9% uptime reliability</li>
                <li>• Scalable to millions of documents</li>
                <li>• Real-time processing pipeline</li>
              </ul>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">Data Quality</h4>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• 95%+ OCR accuracy</li>
                <li>• 90%+ entity recognition precision</li>
                <li>• Automated quality validation</li>
                <li>• Continuous model improvement</li>
              </ul>
            </div>
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200">
              <h4 className="font-semibold text-gray-900 mb-4">Infrastructure</h4>
              <ul className="text-gray-600 space-y-2 text-sm">
                <li>• Cloud-native deployment</li>
                <li>• Kubernetes orchestration</li>
                <li>• Auto-scaling capabilities</li>
                <li>• Enterprise security</li>
              </ul>
            </div>
          </div>
        </section>

        {/* Data Flow Diagram */}
        <section>
          <h3 className="text-2xl font-bold text-gray-900 mb-8 text-center">Data Flow Architecture</h3>
          <div className="bg-white rounded-xl p-8 shadow-sm border border-gray-200">
            <div className="text-center">
              <div className="inline-flex items-center space-x-4 text-sm text-gray-600 mb-4">
                <span className="flex items-center">
                  <div className="w-3 h-3 bg-blue-500 rounded-full mr-2"></div>
                  Input Processing
                </span>
                <span className="flex items-center">
                  <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
                  AI Processing
                </span>
                <span className="flex items-center">
                  <div className="w-3 h-3 bg-purple-500 rounded-full mr-2"></div>
                  Storage Layer
                </span>
                <span className="flex items-center">
                  <div className="w-3 h-3 bg-orange-500 rounded-full mr-2"></div>
                  API Layer
                </span>
              </div>
              
              <div className="text-gray-700 mb-6">
                PDF Documents → OCR Extraction → AI Embeddings → Entity Recognition → Graph Construction → Vector Storage → Search API
              </div>
              
              <p className="text-gray-600 text-sm">
                This linear pipeline ensures high-quality data processing from raw documents to searchable knowledge,
                with each stage validated and optimized for accuracy and performance.
              </p>
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}