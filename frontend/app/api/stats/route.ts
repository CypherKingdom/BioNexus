import { NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function GET() {
  try {
    const response = await fetch(`${BACKEND_URL}/stats`, {
      headers: {
        'Content-Type': 'application/json',
      },
      // Add a timeout to prevent hanging requests
      signal: AbortSignal.timeout(5000)
    })

    if (!response.ok) {
      throw new Error(`Backend responded with status: ${response.status}`)
    }

    const data = await response.json()
    
    return NextResponse.json(data)
  } catch (error) {
    console.error('Failed to fetch stats from backend:', error)
    
    // Return zeros when backend unavailable - NO FAKE DATA
    return NextResponse.json({
      publications: 0,
      pages: 0,
      entities: 0,
      searchIndexSize: 0,
      totalNodes: 0,
      lastUpdated: new Date().toISOString(),
      error: 'Backend unavailable - showing actual zeros'
    })
  }
}