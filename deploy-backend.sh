#!/bin/bash

echo "🚀 Deploying BioNexus Backend to Google Cloud Run..."

# Set the correct PATH for gcloud
export PATH="$PATH:/run/media/CypherKing/Local Disk/BioNexus/google-cloud-sdk/bin"

# Set project
echo "📋 Setting GCP project..."
gcloud config set project coral-field-474212-d2

# Enable required APIs
echo "📡 Enabling Cloud Run API..."
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Navigate to backend directory
cd backend

# Deploy to Cloud Run
echo "🏗️ Deploying backend to Cloud Run..."
gcloud run deploy bionexus-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --max-instances 10 \
  --timeout 3600 \
  --port 8080

# Get the service URL
SERVICE_URL=$(gcloud run services describe bionexus-backend --region=us-central1 --format="value(status.url)")

echo "✅ Backend deployed successfully!"
echo "🌐 Your API is live at: $SERVICE_URL"
echo "📋 API Documentation: $SERVICE_URL/docs"
echo ""
echo "🔗 Next steps:"
echo "1. Test your API at: $SERVICE_URL/stats"
echo "2. Deploy frontend with this backend URL"
echo "3. Configure custom domain bionexus.study"

# Test the deployment
echo ""
echo "🧪 Testing deployment..."
curl -s "$SERVICE_URL/stats" | head -5