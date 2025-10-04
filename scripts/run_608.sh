#!/bin/bash

# BioNexus Full Dataset Ingestion Script
# This script processes all 608 NASA bioscience publications

set -e

echo "🚀 Starting BioNexus Full Dataset Processing..."

# Check if full dataset directory exists
FULL_DATA_DIR="data/full_papers"

if [ ! -d "$FULL_DATA_DIR" ]; then
    echo "❌ Full dataset directory not found: $FULL_DATA_DIR"
    echo "Please ensure the 608 NASA bioscience PDFs are placed in: $FULL_DATA_DIR"
    exit 1
fi

# Count PDF files
PDF_COUNT=$(find "$FULL_DATA_DIR" -name "*.pdf" | wc -l)
echo "📊 Found $PDF_COUNT PDF files in dataset"

if [ "$PDF_COUNT" -eq 0 ]; then
    echo "❌ No PDF files found in $FULL_DATA_DIR"
    exit 1
fi

# Ensure services are running
if ! curl -s http://localhost:8000/health &> /dev/null; then
    echo "❌ Backend API is not running. Please start services first:"
    echo "   ./scripts/run_demo.sh"
    exit 1
fi

echo "⚠️  WARNING: Full dataset processing will:"
echo "   - Process $PDF_COUNT publications"
echo "   - Take several hours to complete" 
echo "   - Use significant computational resources"
echo "   - Require GPU resources for optimal ColPali embeddings"
echo ""

read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo "🔄 Starting full dataset ingestion..."

# Start the ingestion process
RESPONSE=$(curl -s -X POST "http://localhost:8000/ingest/run" \
     -H "Content-Type: application/json" \
     -d '{"mode": "full"}')

JOB_ID=$(echo "$RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('job_id', ''))" 2>/dev/null || echo "")

if [ -z "$JOB_ID" ]; then
    echo "❌ Failed to start ingestion job"
    echo "Response: $RESPONSE"
    exit 1
fi

echo "✅ Ingestion job started with ID: $JOB_ID"
echo "📊 Monitoring progress..."

# Monitor progress
while true; do
    STATUS_RESPONSE=$(curl -s "http://localhost:8000/ingest/status/$JOB_ID")
    
    STATUS=$(echo "$STATUS_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('status', ''))" 2>/dev/null || echo "unknown")
    PROGRESS=$(echo "$STATUS_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('progress', 0))" 2>/dev/null || echo "0")
    PROCESSED=$(echo "$STATUS_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('processed_documents', 0))" 2>/dev/null || echo "0")
    FAILED=$(echo "$STATUS_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('failed_documents', 0))" 2>/dev/null || echo "0")
    
    PROGRESS_PCT=$(echo "$PROGRESS * 100" | bc -l 2>/dev/null || echo "0")
    
    echo "📈 Status: $STATUS | Progress: ${PROGRESS_PCT}% | Processed: $PROCESSED | Failed: $FAILED"
    
    if [ "$STATUS" = "completed" ]; then
        echo "✅ Ingestion completed successfully!"
        break
    elif [ "$STATUS" = "failed" ]; then
        echo "❌ Ingestion failed"
        ERROR=$(echo "$STATUS_RESPONSE" | python3 -c "import json,sys; print(json.load(sys.stdin).get('error_message', 'Unknown error'))" 2>/dev/null || echo "Unknown error")
        echo "Error: $ERROR"
        exit 1
    fi
    
    sleep 30  # Check every 30 seconds
done

echo ""
echo "🎉 Full Dataset Processing Complete!"
echo ""
echo "📊 Final Statistics:"
curl -s "http://localhost:8000/search/stats" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"   Publications: {data.get('total_publications', 0):,}\")
print(f\"   Pages: {data.get('total_pages', 0):,}\")
print(f\"   Entities: {data.get('total_entities', 0):,}\")
print(f\"   Search Index Size: {data.get('search_index_size', 0):,}\")
" 2>/dev/null || echo "   Statistics unavailable"

echo ""
echo "🌐 The full BioNexus knowledge graph is now available at:"
echo "   http://localhost:3000"
echo ""
echo "🔍 You can now:"
echo "   - Search across all 608 publications"
echo "   - Explore the complete knowledge graph"
echo "   - Export comprehensive datasets"
echo "   - Use advanced mission planning features"
echo ""