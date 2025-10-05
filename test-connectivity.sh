#!/bin/bash

# Test connectivity to cloud services with provided credentials
echo "🧪 Testing BioNexus Cloud Connectivity..."
echo "=========================================="

# Test Neo4j Aura connection
echo "🔍 Testing Neo4j Aura connection..."
python3 -c "
import os
try:
    from neo4j import GraphDatabase
    
    uri = 'neo4j+s://e3671855.databases.neo4j.io'
    username = 'neo4j'
    password = 'c8TtugjdTClI-4LEy1LqVWnSDkj6QHbJo61U9I9yNOI'
    
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
    print('❌ Neo4j driver not installed. Run: pip install neo4j')
except Exception as e:
    print(f'❌ Neo4j connection failed: {e}')
"

echo ""

# Test Milvus/Zilliz connection
echo "🔍 Testing Milvus Cloud (Zilliz) connection..."
python3 -c "
try:
    from pymilvus import connections, Collection, utility
    
    uri = 'https://in03-9ec7c214a18d7a5.serverless.aws-eu-central-1.cloud.zilliz.com'
    token = '981a4eaaced7dbb49e0a940d97c7e6d0dd728aedf76bd1e6b7f17c99745dadd425f5d3b02812b4a3b6321a35eb2e8e1d15aa1dcf'
    
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
    print('❌ Milvus client not installed. Run: pip install pymilvus')
except Exception as e:
    print(f'❌ Milvus connection failed: {e}')
"

echo ""
echo "🎯 Connection test completed!"
echo ""
echo "Next steps:"
echo "1. Install dependencies: cd backend && pip install -r requirements.txt"
echo "2. Start backend: cd backend && python -m uvicorn app.main:app --reload"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Access at: http://localhost:3000"