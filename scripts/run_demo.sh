#!/bin/bash

# BioNexus Demo Script
# This script sets up and runs the complete BioNexus demo

set -e  # Exit on any error

echo "🚀 Starting BioNexus Demo Setup..."

# Check if Docker and Docker Compose are available
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Set environment variables
export OPENAI_API_KEY=${OPENAI_API_KEY:-"demo-key-replace-with-real"}

echo "📦 Building and starting services..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Build and start all services
docker-compose -f infra/docker-compose.yml up --build -d

echo "⏳ Waiting for services to be ready..."

# Wait for Neo4j to be ready
echo "Waiting for Neo4j..."
timeout=60
while ! docker exec bionexus-neo4j cypher-shell -u neo4j -p password "RETURN 1;" &> /dev/null; do
    timeout=$((timeout - 1))
    if [ $timeout -le 0 ]; then
        echo "❌ Neo4j failed to start within 60 seconds"
        exit 1
    fi
    sleep 1
done

# Wait for backend API to be ready
echo "Waiting for Backend API..."
timeout=60
while ! curl -s http://localhost:8000/health &> /dev/null; do
    timeout=$((timeout - 1))
    if [ $timeout -le 0 ]; then
        echo "❌ Backend API failed to start within 60 seconds"
        exit 1
    fi
    sleep 1
done

# Wait for frontend to be ready
echo "Waiting for Frontend..."
timeout=60
while ! curl -s http://localhost:3000 &> /dev/null; do
    timeout=$((timeout - 1))
    if [ $timeout -le 0 ]; then
        echo "❌ Frontend failed to start within 60 seconds"
        exit 1
    fi
    sleep 1
done

echo "🔧 Setting up Neo4j schema..."

# Run database setup
docker exec bionexus-neo4j cypher-shell -u neo4j -p password -f /var/lib/neo4j/import/setup.cypher

echo "📊 Running sample data ingestion..."

# Run ingestion for sample papers (if they exist)
if [ -d "data/sample_papers" ] && [ "$(ls -A data/sample_papers/*.pdf 2>/dev/null)" ]; then
    curl -X POST "http://localhost:8000/ingest/run" \
         -H "Content-Type: application/json" \
         -d '{"mode": "sample"}' || echo "⚠️  Ingestion failed - will use sample data from Cypher setup"
else
    echo "⚠️  No sample PDFs found, using mock data from database setup"
fi

echo ""
echo "✅ BioNexus Demo is now running!"
echo ""
echo "🌐 Access the application:"
echo "   Frontend (Main App):    http://localhost:3000"
echo "   Backend API:           http://localhost:8000"
echo "   API Documentation:     http://localhost:8000/docs"
echo "   Neo4j Browser:         http://localhost:7474"
echo "   MinIO Console:         http://localhost:9001"
echo ""
echo "🧪 Demo Features:"
echo "   1. Semantic Search - Try searching for 'microgravity effects'"
echo "   2. Knowledge Graph - Explore entity relationships"
echo "   3. Mission Planner - Get research-based recommendations"
echo "   4. Publication View - Browse detailed paper information"
echo ""
echo "🔑 Login Credentials:"
echo "   Neo4j: neo4j / password"
echo "   MinIO: minioadmin / minioadmin123"
echo ""
echo "📖 To explore the demo:"
echo "   1. Open http://localhost:3000 in your browser"
echo "   2. Try the sample searches provided on the homepage"
echo "   3. Explore the knowledge graph visualization"
echo "   4. Check the mission planner with sample constraints"
echo ""
echo "🛑 To stop the demo:"
echo "   Run: docker-compose -f infra/docker-compose.yml down"
echo ""