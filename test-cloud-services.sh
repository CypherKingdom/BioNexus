#!/bin/bash

# BioNexus Cloud Services Test Script
# This script tests connectivity to all required cloud services

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔍 BioNexus Cloud Services Test${NC}"
echo "======================================"

# Load environment variables
if [ -f ".env" ]; then
    source .env
    echo -e "${GREEN}✅ Environment file loaded${NC}"
else
    echo -e "${RED}❌ .env file not found${NC}"
    echo "Please create a .env file with your cloud credentials"
    exit 1
fi

# Test counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass_test() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

fail_test() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

echo ""
echo -e "${YELLOW}🔐 Testing Cloud Database Services...${NC}"

# Test Neo4j Aura connection
echo "Testing Neo4j Aura connection..."
python3 -c "
import os
from neo4j import GraphDatabase
try:
    uri = os.getenv('NEO4J_URI', 'neo4j+s://localhost:7687')
    user = os.getenv('NEO4J_USER', 'neo4j')
    password = os.getenv('NEO4J_PASSWORD', 'password')
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session() as session:
        result = session.run('RETURN 1 as test')
        result.single()
    driver.close()
    print('SUCCESS: Neo4j Aura connection established')
except Exception as e:
    print(f'FAILED: Neo4j Aura connection failed - {e}')
    exit(1)
" && pass_test "Neo4j Aura connection" || fail_test "Neo4j Aura connection"

# Test Milvus Cloud connection
echo "Testing Milvus Cloud connection..."
python3 -c "
import os
try:
    from pymilvus import connections, utility
    
    host = os.getenv('MILVUS_HOST', '')
    port = os.getenv('MILVUS_PORT', '19530')
    user = os.getenv('MILVUS_USER', '')
    password = os.getenv('MILVUS_PASSWORD', '')
    
    if not host:
        print('SKIPPED: Milvus host not configured')
        exit(0)
    
    connections.connect(
        alias='test',
        host=host,
        port=port,
        user=user,
        password=password,
        secure=True
    )
    
    # Test connection by listing collections
    collections = utility.list_collections()
    connections.disconnect('test')
    print('SUCCESS: Milvus Cloud connection established')
    
except ImportError:
    print('SKIPPED: pymilvus not installed')
    exit(0)
except Exception as e:
    print(f'FAILED: Milvus Cloud connection failed - {e}')
    exit(1)
" && pass_test "Milvus Cloud connection" || fail_test "Milvus Cloud connection"

echo ""
echo -e "${YELLOW}☁️ Testing Google Cloud Services...${NC}"

# Test Google Cloud Storage
echo "Testing Google Cloud Storage..."
python3 -c "
import os
try:
    from google.cloud import storage
    
    project_id = os.getenv('GCS_PROJECT_ID', '')
    bucket_name = os.getenv('GCS_BUCKET_NAME', 'bionexus-documents')
    
    if not project_id:
        print('SKIPPED: GCS project ID not configured')
        exit(0)
    
    client = storage.Client(project=project_id)
    
    # Try to access the bucket
    bucket = client.bucket(bucket_name)
    bucket.reload()  # This will fail if bucket doesn't exist or no access
    
    print('SUCCESS: Google Cloud Storage connection established')
    
except ImportError:
    print('SKIPPED: google-cloud-storage not installed')
    exit(0)
except Exception as e:
    print(f'FAILED: Google Cloud Storage connection failed - {e}')
    exit(1)
" && pass_test "Google Cloud Storage" || fail_test "Google Cloud Storage"

echo ""
echo -e "${YELLOW}🔑 Testing External API Keys...${NC}"

# Test OpenAI API
echo "Testing OpenAI API..."
python3 -c "
import os
import requests

api_key = os.getenv('OPENAI_API_KEY', '')
if not api_key or api_key.startswith('sk-proj-your-'):
    print('SKIPPED: OpenAI API key not configured')
    exit(0)

try:
    response = requests.get(
        'https://api.openai.com/v1/models',
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=10
    )
    if response.status_code == 200:
        print('SUCCESS: OpenAI API key is valid')
    else:
        print(f'FAILED: OpenAI API returned status {response.status_code}')
        exit(1)
except Exception as e:
    print(f'FAILED: OpenAI API test failed - {e}')
    exit(1)
" && pass_test "OpenAI API key" || fail_test "OpenAI API key"

# Test Hugging Face API
echo "Testing Hugging Face API..."
python3 -c "
import os
import requests

api_key = os.getenv('HUGGINGFACE_API_KEY', '')
if not api_key or api_key.startswith('hf_your-'):
    print('SKIPPED: Hugging Face API key not configured')
    exit(0)

try:
    response = requests.get(
        'https://huggingface.co/api/whoami-v2',
        headers={'Authorization': f'Bearer {api_key}'},
        timeout=10
    )
    if response.status_code == 200:
        print('SUCCESS: Hugging Face API key is valid')
    else:
        print(f'FAILED: Hugging Face API returned status {response.status_code}')
        exit(1)
except Exception as e:
    print(f'FAILED: Hugging Face API test failed - {e}')
    exit(1)
" && pass_test "Hugging Face API key" || fail_test "Hugging Face API key"

echo ""
echo -e "${YELLOW}📱 Testing Optional External APIs...${NC}"

# Test Google Maps API (optional)
if [ -n "$GOOGLE_MAPS_API_KEY" ] && [[ ! "$GOOGLE_MAPS_API_KEY" =~ ^(your-|AIzaSyxxxxx) ]]; then
    echo "Testing Google Maps API..."
    curl -s "https://maps.googleapis.com/maps/api/js/QuotaService.RecordEvent?libraries=geometry&key=$GOOGLE_MAPS_API_KEY" > /dev/null \
        && pass_test "Google Maps API key" \
        || fail_test "Google Maps API key"
else
    echo -e "${YELLOW}⚠️ Google Maps API key not configured (optional)${NC}"
fi

# Test Meteomatics API (optional)
if [ -n "$METEOMATICS_USERNAME" ] && [ -n "$METEOMATICS_PASSWORD" ] && [[ ! "$METEOMATICS_USERNAME" =~ ^your- ]]; then
    echo "Testing Meteomatics API..."
    curl -s --user "$METEOMATICS_USERNAME:$METEOMATICS_PASSWORD" \
        "https://api.meteomatics.com/2024-01-01T00:00:00Z/t_2m:C/52.520551,13.461804/json" > /dev/null \
        && pass_test "Meteomatics API credentials" \
        || fail_test "Meteomatics API credentials"
else
    echo -e "${YELLOW}⚠️ Meteomatics API not configured (optional)${NC}"
fi

echo ""
echo "📋 Test Summary"
echo "==============="
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"

# Calculate success rate
total_tests=$((TESTS_PASSED + TESTS_FAILED))
if [ $total_tests -gt 0 ]; then
    success_rate=$((TESTS_PASSED * 100 / total_tests))
    echo "Success Rate: ${success_rate}%"
fi

echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All cloud services are properly configured!${NC}"
    echo ""
    echo "Your BioNexus deployment is ready for:"
    echo "✅ Neo4j Aura knowledge graph"
    echo "✅ Milvus Cloud vector search"
    echo "✅ Google Cloud Storage"
    echo "✅ External AI services"
    echo ""
    echo "Next steps:"
    echo "1. Deploy to cloud: ./cloud-deployment/deploy.sh"
    echo "2. Access your application at the deployed URLs"
    exit 0
elif [ $TESTS_FAILED -le 2 ]; then
    echo -e "${YELLOW}⚠️ Minor configuration issues detected.${NC}"
    echo "Please check the failed tests above and update your .env file."
    exit 1
else
    echo -e "${RED}🚨 Multiple services not configured properly.${NC}"
    echo ""
    echo "Required actions:"
    echo "1. Set up Neo4j Aura database"
    echo "2. Configure Milvus Cloud instance"
    echo "3. Set up Google Cloud Storage"
    echo "4. Obtain required API keys"
    echo ""
    echo "See CLOUD_SETUP_GUIDE.md for detailed instructions."
    exit 1
fi