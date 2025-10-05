#!/bin/bash

# Quick Google Cloud deployment status checker
export PATH="$PATH:/run/media/CypherKing/Local Disk/BioNexus/google-cloud-sdk/bin"

echo "📊 BioNexus Google Cloud Status"
echo "================================"

# Check backend service
echo "🔗 Backend Service:"
gcloud run services describe bionexus-backend --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "   ⏳ Still deploying..."

# Check frontend service  
echo "🌐 Frontend Service:"
gcloud run services describe bionexus-frontend --region=us-central1 --format="value(status.url)" 2>/dev/null || echo "   ⏳ Waiting for backend..."

echo ""
echo "🔄 Run this script anytime to check status: ./check-status.sh"