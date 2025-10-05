import { NextRequest, NextResponse } from 'next/server'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000'

export async function GET(request: NextRequest) {
  const searchParams = request.nextUrl.searchParams
  const query = searchParams.get('q')

  if (!query || query.length < 2) {
    return NextResponse.json({ suggestions: [] })
  }

  try {
    // Try to get suggestions from backend
    const response = await fetch(`${BACKEND_URL}/search/suggestions?q=${encodeURIComponent(query)}`, {
      headers: {
        'Content-Type': 'application/json',
      },
      signal: AbortSignal.timeout(3000)
    })

    if (response.ok) {
      const data = await response.json()
      return NextResponse.json(data)
    }
  } catch (error) {
    console.error('Backend suggestions unavailable:', error)
  }

  // Fallback suggestions based on common bioscience terms
  const fallbackSuggestions = [
    'microgravity effects on cells', 
    'space radiation exposure',
    'cardiovascular adaptation',
    'bone density changes',
    'plant growth in space',
    'protein crystallization',
    'cell culture experiments',
    'tissue engineering',
    'muscle atrophy',
    'osteoporosis prevention',
    'neural adaptation',
    'circadian rhythm disruption',
    'immune system changes',
    'wound healing in space',
    'drug delivery systems'
  ].filter(suggestion => 
    suggestion.toLowerCase().includes(query.toLowerCase())
  ).slice(0, 5)

  return NextResponse.json({ 
    suggestions: fallbackSuggestions,
    fallback: true
  })
}