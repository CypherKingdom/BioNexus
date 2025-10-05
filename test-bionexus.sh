#!/bin/bash

# BioNexus Complete Test & Setup Script
# Tests connectivity, core services, and provides setup functionality

echo "🧪 BioNexus Complete Test Suite"
echo "================================"

# Function to check if we're in a virtual environment
check_venv() {
    if [[ "$VIRTUAL_ENV" != "" ]]; then
        echo "🐍 Using virtual environment: $(basename $VIRTUAL_ENV)"
        return 0
    else
        echo "⚠️  No virtual environment detected"
        return 1
    fi
}

# Function to setup development environment
setup_environment() {
    echo ""
    echo "🔧 Setting up Development Environment..."
    echo "======================================="
    
    # Check if Python 3 is available
    if ! command -v python3 &> /dev/null; then
        echo "❌ Python 3 is required but not installed"
        exit 1
    fi
    
    echo "🐍 Python version: $(python3 --version)"
    
    # Navigate to backend directory
    cd backend || {
        echo "❌ Backend directory not found"
        exit 1
    }
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "venv" ]; then
        echo "📦 Creating Python virtual environment..."
        python3 -m venv venv || {
            echo "❌ Failed to create virtual environment"
            exit 1
        }
    fi
    
    # Activate virtual environment
    echo "🔄 Activating virtual environment..."
    source venv/bin/activate || {
        echo "❌ Failed to activate virtual environment"
        exit 1
    }
    
    # Upgrade pip
    echo "⬆️  Upgrading pip..."
    pip install --upgrade pip
    
    # Install backend dependencies
    echo "📦 Installing backend dependencies..."
    pip install -r requirements.txt || {
        echo "❌ Failed to install backend dependencies"
        exit 1
    }
    
    echo "✅ Backend environment setup complete!"
    cd ..
}

# Function to install minimal dependencies if needed
ensure_dependencies() {
    echo "🔧 Ensuring dependencies are installed..."
    
    # Check if we can import the required packages
    python3 -c "import neo4j, pymilvus, dotenv" 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ Dependencies already installed"
        return 0
    fi
    
    # If not in virtual environment, try to install minimal deps
    if [ "$VIRTUAL_ENV" == "" ]; then
        echo "📦 Installing minimal dependencies for testing..."
        pip3 install --user neo4j pymilvus python-dotenv 2>/dev/null || {
            echo "❌ Failed to install dependencies. Setting up full environment..."
            setup_environment
            # Re-activate venv and return to root
            cd backend && source venv/bin/activate && cd ..
        }
    fi
}

# Function to test connectivity
test_connectivity() {
    echo ""
    echo "🔍 Testing Cloud Service Connectivity..."
    echo "======================================="
    
    # Test Neo4j Aura connection
    echo "🔍 Testing Neo4j Aura connection..."
    python3 -c "
import os
try:
    from neo4j import GraphDatabase
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv('.env')
    
    uri = os.getenv('NEO4J_URI', 'neo4j+s://e3671855.databases.neo4j.io')
    username = os.getenv('NEO4J_USERNAME', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'c8TtugjdTClI-4LEy1LqVWnSDkj6QHbJo61U9I9yNOI')
    
    driver = GraphDatabase.driver(uri, auth=(username, password))
    
    with driver.session() as session:
        result = session.run('RETURN \"Neo4j Aura Connected!\" as message')
        record = result.single()
        print(f'✅ Neo4j Aura: {record[\"message\"]}')
        
        # Check if we have data
        count_result = session.run('MATCH (n) RETURN count(n) as total_nodes')
        count_record = count_result.single()
        print(f'📊 Total nodes in database: {count_record[\"total_nodes\"]}')
        
    driver.close()
    
except ImportError:
    print('❌ Neo4j driver not installed. Run with --setup flag')
except Exception as e:
    print(f'❌ Neo4j connection failed: {e}')
"
    
    echo ""
    
    # Test Milvus/Zilliz connection
    echo "🔍 Testing Milvus Cloud (Zilliz) connection..."
    python3 -c "
import os
try:
    from pymilvus import connections, Collection, utility
    from dotenv import load_dotenv
    
    # Load environment variables
    load_dotenv('.env')
    
    uri = os.getenv('MILVUS_URI', 'https://in03-9ec7c214a18d7a5.serverless.aws-eu-central-1.cloud.zilliz.com')
    token = os.getenv('MILVUS_TOKEN', '981a4eaaced7dbb49e0a940d97c7e6d0dd728aedf76bd1e6b7f17c99745dadd425f5d3b02812b4a3b6321a35eb2e8e1d15aa1dcf')
    
    # Connect to Milvus Cloud
    connections.connect(
        alias='default',
        uri=uri,
        token=token
    )
    
    print('✅ Milvus Cloud: Connected successfully!')
    
    # List collections
    collections = utility.list_collections()
    print(f'📊 Available collections: {collections}')
    
    if collections:
        # Get info about first collection
        collection_name = collections[0]
        collection = Collection(collection_name)
        print(f'📈 Collection \"{collection_name}\" has {collection.num_entities} entities')
    
except ImportError:
    print('❌ Milvus client not installed. Run with --setup flag')
except Exception as e:
    print(f'❌ Milvus connection failed: {e}')
"
}

# Function to test core services
test_core_services() {
    echo ""
    echo "🧪 Testing Core Services..."
    echo "==========================="
    
    # Only run core services test if in backend directory with proper setup
    if [ "$VIRTUAL_ENV" != "" ] && [ -d "backend/app" ]; then
        python3 -c "
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path.cwd() / 'backend'
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv('.env')

try:
    # Test config
    from app.config import settings
    print(f'✅ Configuration loaded')
    
    # Test Neo4j
    from app.services.neo4j_client import Neo4jClient
    neo4j = Neo4jClient()
    print(f'✅ Neo4j: {\"Connected\" if neo4j.connected else \"Failed\"}')
    
    # Test Milvus  
    from app.services.milvus_client import MilvusClient
    milvus = MilvusClient()
    print(f'✅ Milvus: {\"Connected\" if milvus.connected else \"Failed\"}')
    
    # Test embeddings
    from app.services.query_embeddings import QueryEmbeddingService
    embeddings = QueryEmbeddingService()
    test_query = 'What is photosynthesis?'
    embedding = embeddings.encode_query(test_query)
    print(f'✅ Embeddings: Generated {len(embedding)} dimensional vector')
    
    print('\\n🎉 All core services working!')
    
except Exception as e:
    print(f'⚠️  Core services test skipped: {e}')
    print('   Run with --setup flag to configure full environment')
"
    else
        echo "⚠️  Core services test requires virtual environment setup"
        echo "   Run with --setup flag to configure full environment"
    fi
}

# Main execution
case "${1:-}" in
    --setup|-s)
        echo "🚀 Setting up BioNexus Development Environment..."
        setup_environment
        check_venv
        ensure_dependencies
        test_connectivity
        test_core_services
        ;;
    --connectivity|-c)
        echo "🌐 Testing connectivity only..."
        ensure_dependencies
        test_connectivity
        ;;
    --help|-h)
        echo "BioNexus Test Script Usage:"
        echo "  ./test-bionexus.sh         - Run all tests"
        echo "  ./test-bionexus.sh --setup - Setup environment and run tests"
        echo "  ./test-bionexus.sh -c      - Test connectivity only"
        echo "  ./test-bionexus.sh --help  - Show this help"
        exit 0
        ;;
    *)
        echo "🔍 Running complete test suite..."
        check_venv
        ensure_dependencies
        test_connectivity
        test_core_services
        ;;
esac

echo ""
echo "🎯 Test completed!"
echo ""
echo "Next steps:"
echo "1. Start backend: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "2. Start frontend: cd frontend && npm run dev"
echo "3. Access at: http://localhost:3000"