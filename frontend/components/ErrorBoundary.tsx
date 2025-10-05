'use client'

import React from 'react'

interface ErrorBoundaryProps {
  children: React.ReactNode
  fallback?: React.ReactNode
}

interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return this.props.fallback || (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <div className="text-red-600 font-medium mb-2">Something went wrong</div>
          <p className="text-red-700 text-sm mb-4">
            {this.state.error?.message || 'An unexpected error occurred'}
          </p>
          <button
            onClick={() => this.setState({ hasError: false, error: undefined })}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 text-sm"
          >
            Try Again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}

// Hook-based error boundary for functional components
export function useErrorHandler() {
  return (error: Error, errorInfo?: { componentStack: string }) => {
    console.error('Error caught by error handler:', error, errorInfo)
  }
}

// Safe render function to handle potentially problematic objects
export function safeRender(value: any): string {
  try {
    if (value === null || value === undefined) {
      return 'N/A'
    }
    if (typeof value === 'string') {
      return value
    }
    if (typeof value === 'number' || typeof value === 'boolean') {
      return String(value)
    }
    if (Array.isArray(value)) {
      return value.map(safeRender).join(', ')
    }
    if (typeof value === 'object') {
      // Check if it's the problematic {text, type, score} object
      if ('text' in value && 'type' in value && 'score' in value) {
        console.error('CRITICAL: Detected problematic object with {text, type, score}:', value)
        console.error('Stack trace:', new Error().stack)
        return String(value.text || value.type || 'Object')
      }
      // Check for other potentially problematic object structures
      if (typeof value === 'object' && value.constructor === Object) {
        const keys = Object.keys(value)
        if (keys.length <= 5) {
          return JSON.stringify(value)
        } else {
          return `{${keys.length} properties}`
        }
      }
      return JSON.stringify(value)
    }
    return String(value)
  } catch (e) {
    console.error('Error in safeRender:', e, 'value:', value)
    return 'Invalid data'
  }
}

// Deep object validator to catch problematic objects before they reach React
export function validateForReact(obj: any, path = 'root'): any {
  if (obj === null || obj === undefined) {
    return obj
  }
  
  if (typeof obj === 'string' || typeof obj === 'number' || typeof obj === 'boolean') {
    return obj
  }
  
  if (Array.isArray(obj)) {
    return obj.map((item, index) => validateForReact(item, `${path}[${index}]`))
  }
  
  if (typeof obj === 'object') {
    // Check for the specific problematic pattern
    if ('text' in obj && 'type' in obj && 'score' in obj) {
      console.error(`CRITICAL: Found {text, type, score} object at ${path}:`, obj)
      throw new Error(`Problematic object detected at ${path}: {text, type, score}`)
    }
    
    // Recursively validate all properties
    const validated: any = {}
    for (const [key, value] of Object.entries(obj)) {
      validated[key] = validateForReact(value, `${path}.${key}`)
    }
    return validated
  }
  
  return obj
}