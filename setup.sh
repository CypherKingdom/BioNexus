#!/bin/bash

# BioNexus Project Setup Script
# This script sets up the entire BioNexus project including all services

set -e

echo "🌟 Welcome to BioNexus Setup!"
echo "================================="

# Check for required tools
check_tool() {
  if ! command -v $1 &> /dev/null; then
    echo "❌ $1 is not installed. Please install it first."
    return 1
  fi
  echo "✅ $1 is available"
  return 0
}

echo "🔍 Checking required tools..."
check_tool "docker" || exit 1
check_tool "docker-compose" || exit 1
check_tool "python3" || exit 1
check_tool "node" || exit 1

# Check if we're in the project root
if [ ! -f "docker-compose.yml" ]; then
  echo "❌ Error: docker-compose.yml not found. Please run this script from the project root."
  exit 1
fi

echo ""
echo "📦 Setting up project structure..."

# Create necessary directories
mkdir -p data/{neo4j,weaviate,minio,uploads,processed,embeddings,exports}
mkdir -p logs
mkdir -p sample_data

# Set permissions
chmod 755 data
chmod 755 logs
chmod 755 sample_data

echo ""
echo "⚙️ Setting up environment files..."

# Create root .env if it doesn't exist
if [ ! -f ".env" ]; then
  cp .env.example .env
  echo "📝 Created .env from template. Please review and update the settings."
fi

# Setup backend
echo ""
echo "🐍 Setting up backend..."
cd backend
if [ -f "setup.sh" ]; then
  ./setup.sh
else
  echo "⚠️ Backend setup script not found, running basic setup..."
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  pip install -r requirements.txt
fi
cd ..

# Setup frontend
echo ""
echo "⚛️ Setting up frontend..."
cd frontend
if [ -f "setup.sh" ]; then
  ./setup.sh
else
  echo "⚠️ Frontend setup script not found, running basic setup..."
  if command -v pnpm &> /dev/null; then
    pnpm install
  elif command -v yarn &> /dev/null; then
    yarn install
  else
    npm install
  fi
fi
cd ..

echo ""
echo "🐳 Setting up Docker services..."

# Pull Docker images
docker-compose pull

# Create Docker networks
docker network create bionexus-network 2>/dev/null || echo "Network already exists"

echo ""
echo "🔧 Making scripts executable..."
find scripts -name "*.sh" -type f -exec chmod +x {} \; 2>/dev/null || echo "Scripts directory not found"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 Next steps:"
echo "1. Review and update .env files as needed"
echo "2. Start services: docker-compose up -d"
echo "3. Initialize database: docker-compose exec neo4j cypher-shell -u neo4j -p password -f /setup/cypher_setup.cypher"
echo "4. Run demo: ./scripts/run_demo.sh"
echo ""
echo "📚 Documentation:"
echo "- Frontend: http://localhost:3000"
echo "- Backend API: http://localhost:8000"
echo "- API Docs: http://localhost:8000/docs"
echo "- Neo4j Browser: http://localhost:7474"
echo ""
echo "🎉 BioNexus is ready to use!"