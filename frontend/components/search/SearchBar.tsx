'use client'

import { useState, useEffect } from 'react'
import { SearchIcon, FilterIcon } from 'lucide-react'
import { cn } from '@/lib/utils'

interface SearchBarProps {
  value: string
  onChange: (value: string) => void
  placeholder?: string
  size?: 'default' | 'large'
  onSearch?: () => void
  showFilters?: boolean
  className?: string
}

export function SearchBar({
  value,
  onChange,
  placeholder = "Search publications, entities, concepts...",
  size = 'default',
  onSearch,
  showFilters = false,
  className
}: SearchBarProps) {
  const [suggestions, setSuggestions] = useState<string[]>([])
  const [showSuggestions, setShowSuggestions] = useState(false)

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    onSearch?.()
    setShowSuggestions(false)
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Escape') {
      setShowSuggestions(false)
    }
  }

  // Fetch suggestions when value changes
  useEffect(() => {
    if (value.length > 2) {
      const fetchSuggestions = async () => {
        try {
          const response = await fetch(`/api/search/suggestions?q=${encodeURIComponent(value)}`)
          if (response.ok) {
            const data = await response.json()
            setSuggestions(data.suggestions || [])
            setShowSuggestions(true)
          } else {
            // Fallback to mock suggestions
            const mockSuggestions = [
              'microgravity effects on cells',
              'space radiation exposure',
              'cardiovascular adaptation',
              'bone density changes',
              'plant growth in space'
            ].filter(suggestion => 
              suggestion.toLowerCase().includes(value.toLowerCase())
            )
            setSuggestions(mockSuggestions)
            setShowSuggestions(true)
          }
        } catch (error) {
          console.error('Failed to fetch suggestions:', error)
          // Use fallback suggestions on error
          const mockSuggestions = [
            'microgravity effects on cells',
            'space radiation exposure',
            'cardiovascular adaptation',
            'bone density changes',
            'plant growth in space'
          ].filter(suggestion => 
            suggestion.toLowerCase().includes(value.toLowerCase())
          )
          setSuggestions(mockSuggestions)
          setShowSuggestions(true)
        }
      }

      // Debounce the search
      const timeoutId = setTimeout(fetchSuggestions, 300)
      return () => clearTimeout(timeoutId)
    } else {
      setSuggestions([])
      setShowSuggestions(false)
    }
  }, [value])

  const sizeClasses = {
    default: 'h-12',
    large: 'h-16 text-lg'
  }

  return (
    <div className={cn("relative w-full", className)}>
      <form onSubmit={handleSubmit} className="relative">
        <div className="relative flex items-center">
          <SearchIcon className={cn(
            "absolute left-4 text-gray-400",
            size === 'large' ? 'w-6 h-6' : 'w-5 h-5'
          )} />
          
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
            placeholder={placeholder}
            className={cn(
              "w-full bg-white border border-gray-300 rounded-xl shadow-sm focus:ring-2 focus:ring-primary-300 focus:border-primary-500 outline-none transition-all duration-200",
              sizeClasses[size],
              size === 'large' ? 'pl-14 pr-20' : 'pl-12 pr-16'
            )}
          />
          
          <div className="absolute right-2 flex items-center space-x-2">
            {showFilters && (
              <button
                type="button"
                className="p-2 text-gray-400 hover:text-gray-600 rounded-lg transition-colors"
                title="Filters"
              >
                <FilterIcon className="w-5 h-5" />
              </button>
            )}
            
            <button
              type="submit"
              className={cn(
                "bg-primary-500 hover:bg-primary-600 text-white rounded-lg transition-colors flex items-center justify-center",
                size === 'large' ? 'w-12 h-12' : 'w-10 h-10'
              )}
            >
              <SearchIcon className={cn(
                "text-white",
                size === 'large' ? 'w-6 h-6' : 'w-5 h-5'
              )} />
            </button>
          </div>
        </div>

        {/* Suggestions Dropdown */}
        {showSuggestions && suggestions.length > 0 && (
          <div className="absolute top-full left-0 right-0 mt-2 bg-white border border-gray-200 rounded-xl shadow-lg z-50 max-h-64 overflow-y-auto">
            {suggestions.map((suggestion, index) => (
              <button
                key={index}
                type="button"
                onClick={() => {
                  onChange(suggestion)
                  setShowSuggestions(false)
                  onSearch?.()
                }}
                className="w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center space-x-3 border-b border-gray-100 last:border-b-0"
              >
                <SearchIcon className="w-4 h-4 text-gray-400" />
                <span className="text-gray-700">{suggestion}</span>
              </button>
            ))}
          </div>
        )}
      </form>
    </div>
  )
}