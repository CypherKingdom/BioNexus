'use client'

import React, { useState, useEffect } from 'react'
import { SearchIcon, FilterIcon, BookOpenIcon, TagIcon, CalendarIcon } from 'lucide-react'
import Link from 'next/link'
import { SearchBar } from '@/components/search/SearchBar'
import { ErrorBoundary, safeRender, validateForReact } from '@/components/ErrorBoundary'

interface SearchResult {
  id: string
  title: string
  authors: string[]
  year: number
  abstract: string
  score: number
  entities: string[]
  pub_id: string
}

export default function SearchPage() {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState<SearchResult[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [totalResults, setTotalResults] = useState(0)

  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) {
      setResults([])
      setTotalResults(0)
      return
    }

    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/search/semantic', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: searchQuery,
          top_k: 20
        })
      })

      if (response.ok) {
        const data = await response.json()
        
        // Validate the data structure before processing
        try {
          validateForReact(data, 'searchResponse')
        } catch (error) {
          console.error('Search response validation failed:', error)
          setError('Invalid data structure received from server')
          return
        }
        
        // Clean the results to ensure all fields are properly serialized
        const cleanResults = (data.results || []).map((result: any) => {
          // Clean entities array
          const cleanEntities: string[] = []
          if (Array.isArray(result.entities)) {
            result.entities.forEach((entity: any) => {
              try {
                if (typeof entity === 'string') {
                  cleanEntities.push(entity)
                } else if (entity && typeof entity === 'object') {
                  const entityStr = (entity as any).text || (entity as any).name || (entity as any).type || 'Entity'
                  cleanEntities.push(String(entityStr))
                } else {
                  cleanEntities.push(String(entity || 'Entity'))
                }
              } catch (e) {
                cleanEntities.push('Entity')
              }
            })
          }
          
          // Clean authors array
          const cleanAuthors: string[] = []
          if (Array.isArray(result.authors)) {
            result.authors.forEach((author: any) => {
              try {
                if (typeof author === 'string') {
                  cleanAuthors.push(author)
                } else if (author && typeof author === 'object') {
                  cleanAuthors.push(String((author as any).name || 'Unknown Author'))
                } else {
                  cleanAuthors.push(String(author || 'Unknown Author'))
                }
              } catch (e) {
                cleanAuthors.push('Unknown Author')
              }
            })
          }
          
          return {
            id: String(result.id || ''),
            title: String(result.title || 'Untitled'),
            authors: cleanAuthors,
            year: Number(result.year) || new Date().getFullYear(),
            abstract: String(result.abstract || ''),
            score: Number(result.score) || 0,
            entities: cleanEntities,
            pub_id: String(result.pub_id || result.id || '')
          }
        })
        
        setResults(cleanResults)
        setTotalResults(Number(data.total_results) || 0)
      } else {
        setError('Search service unavailable')
        setResults([])
        setTotalResults(0)
      }
    } catch (err) {
      console.error('Search failed:', err)
      setError('Unable to perform search - backend unavailable')
      setResults([])
      setTotalResults(0)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    const delayedSearch = setTimeout(() => {
      if (query) {
        performSearch(query)
      }
    }, 500)

    return () => clearTimeout(delayedSearch)
  }, [query])

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <Link href="/" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-500 rounded-lg flex items-center justify-center">
                <SearchIcon className="w-5 h-5 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900">BioNexus Search</h1>
            </Link>
            <nav className="hidden md:flex space-x-6">
              <Link href="/" className="text-gray-600 hover:text-primary-700 transition-colors">Home</Link>
              <Link href="/knowledge-graph" className="text-gray-600 hover:text-primary-700 transition-colors">Knowledge Graph</Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Search Section */}
        <div className="mb-8">
          <div className="max-w-4xl mx-auto">
            <h2 className="text-3xl font-bold text-gray-900 text-center mb-6">
              Search NASA Bioscience Publications
            </h2>
            <p className="text-gray-600 text-center mb-8">
              Use natural language to find relevant research papers, experiments, and biological findings
            </p>
            
            <SearchBar
              value={query}
              onChange={setQuery}
              placeholder="Search for research topics, organisms, experiments..."
              size="large"
              showFilters={true}
              onSearch={() => performSearch(query)}
            />
          </div>
        </div>

        {/* Results Section */}
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Filters Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 sticky top-8">
              <h3 className="font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <FilterIcon className="w-5 h-5" />
                Filters
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Publication Year
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-500">
                    <option value="">All Years</option>
                    <option value="2023">2023</option>
                    <option value="2022">2022</option>
                    <option value="2021">2021</option>
                    <option value="2020">2020</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Research Area
                  </label>
                  <select className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-300 focus:border-primary-500">
                    <option value="">All Areas</option>
                    <option value="microgravity">Microgravity</option>
                    <option value="radiation">Radiation</option>
                    <option value="cell-biology">Cell Biology</option>
                    <option value="plant-biology">Plant Biology</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Results Area */}
          <div className="lg:col-span-3">
            {/* Results Header */}
            {(query || results.length > 0) && (
              <div className="mb-6">
                <div className="flex items-center justify-between">
                  <h3 className="text-lg font-semibold text-gray-900">
                    {loading ? (
                      <span className="flex items-center gap-2">
                        <div className="w-4 h-4 border-2 border-primary-500 border-t-transparent rounded-full animate-spin"></div>
                        Searching...
                      </span>
                    ) : error ? (
                      <span className="text-red-600">Search Error</span>
                    ) : (
                      `${totalResults} results for "${query}"`
                    )}
                  </h3>
                </div>
              </div>
            )}

            {/* Error State */}
            {error && (
              <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                <div className="text-red-600 font-medium mb-2">Search Unavailable</div>
                <p className="text-red-700 text-sm">{error}</p>
                <p className="text-red-600 text-sm mt-2">
                  Please ensure the backend server is running on port 8000
                </p>
              </div>
            )}

            {/* No Results State */}
            {!loading && !error && query && results.length === 0 && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
                <SearchIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">No results found</h3>
                <p className="text-gray-600">
                  Try different keywords or check if the backend is connected to the database
                </p>
              </div>
            )}

            {/* Results List */}
            <div className="space-y-4">
              {results.map((result, index) => {
                // Ensure result is properly serialized
                const safeResult = {
                  id: safeRender(result?.id || index),
                  title: safeRender(result?.title || 'Untitled Publication'),
                  authors: Array.isArray(result?.authors) ? result.authors.map(a => safeRender(a || 'Unknown')) : [],
                  year: Number(result?.year) || new Date().getFullYear(),
                  abstract: safeRender(result?.abstract || ''),
                  score: Number(result?.score) || 0,
                  entities: Array.isArray(result?.entities) ? result.entities.map(e => safeRender(e || 'Entity')) : [],
                  pub_id: safeRender(result?.pub_id || result?.id || 'unknown')
                };
                
                return (
                <ErrorBoundary key={safeResult.id}>
                <div
                  className="bg-white rounded-xl p-6 shadow-sm border border-gray-200 hover:shadow-md hover:border-primary-200 transition-all duration-200"
                >
                  <div className="flex items-start justify-between mb-3">
                    <h4 className="text-lg font-semibold text-gray-900 hover:text-primary-700 cursor-pointer line-clamp-2">
                      {safeResult.title}
                    </h4>
                    <div className="ml-4 flex-shrink-0">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-primary-100 text-primary-800">
                        {Math.round(safeResult.score * 100)}% match
                      </span>
                    </div>
                  </div>

                  <div className="flex items-center text-sm text-gray-600 mb-3 space-x-4">
                    <span className="flex items-center gap-1">
                      <BookOpenIcon className="w-4 h-4" />
                      {safeResult.authors.length > 0 ? 
                        safeResult.authors.slice(0, 3).join(', ') : 'Unknown authors'}
                      {safeResult.authors.length > 3 && ` +${safeResult.authors.length - 3} more`}
                    </span>
                    {safeResult.year && (
                      <span className="flex items-center gap-1">
                        <CalendarIcon className="w-4 h-4" />
                        {safeResult.year}
                      </span>
                    )}
                  </div>

                  <p className="text-gray-700 text-sm mb-4 line-clamp-3">
                    {safeResult.abstract}
                  </p>

                  {safeResult.entities.length > 0 && (
                    <div className="flex items-center gap-2 mb-3">
                      <TagIcon className="w-4 h-4 text-gray-400" />
                      <div className="flex flex-wrap gap-1">
                        {safeResult.entities.slice(0, 5).map((entity, entityIndex) => (
                          <span
                            key={entityIndex}
                            className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800"
                          >
                            {entity}
                          </span>
                        ))}
                        {safeResult.entities.length > 5 && (
                          <span className="text-xs text-gray-500">
                            +{safeResult.entities.length - 5} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  <div className="flex items-center justify-between pt-3 border-t border-gray-100">
                    <span className="text-xs text-gray-500">
                      ID: {safeResult.pub_id}
                    </span>
                    <button className="text-primary-600 hover:text-primary-700 text-sm font-medium transition-colors">
                      View Details →
                    </button>
                  </div>
                </div>
                </ErrorBoundary>
                );
              })}
            </div>

            {/* Load More */}
            {results.length > 0 && results.length < totalResults && (
              <div className="text-center mt-8">
                <button className="btn-outline">
                  Load More Results
                </button>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  )
}