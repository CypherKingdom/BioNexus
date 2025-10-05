#!/bin/bash

echo "🚀 Deploying BioNexus to Google Cloud Run..."

# Set the correct PATH for gcloud
export PATH="$PATH:/run/media/CypherKing/Local Disk/BioNexus/google-cloud-sdk/bin"

# Set project
gcloud config set project coral-field-474212-d2

# Enable required APIs
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy backend to Cloud Run
echo "🏗️ Deploying backend to Cloud Run..."
cd backend

gcloud run deploy bionexus-backend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --max-instances 10 \
  --timeout 3600 \
  --port 8080 \
  --set-env-vars="NEO4J_URI=neo4j+s://e3671855.databases.neo4j.io,NEO4J_USERNAME=neo4j,NEO4J_PASSWORD=c8TtugjdTClI-4LEy1LqVWnSDkj6QHbJo61U9I9yNOI,NEO4J_DATABASE=neo4j,MILVUS_URI=https://in03-9ec7c214a18d7a5.serverless.aws-eu-central-1.cloud.zilliz.com,MILVUS_TOKEN=981a4eaaced7dbb49e0a940d97c7e6d0dd728aedf76bd1e6b7f17c99745dadd425f5d3b02812b4a3b6321a35eb2e8e1d15aa1dcf,MILVUS_COLLECTION_NAME=bionexus_embeddings,MILVUS_SECURE=true,AZURE_TEXT_ANALYTICS_ENDPOINT=https://eastus.api.cognitive.microsoft.com/,AZURE_TEXT_ANALYTICS_KEY=91763b26b4ed446c8f77b982ff4a9ed8,AZURE_COMPUTER_VISION_ENDPOINT=https://eastus.api.cognitive.microsoft.com/,AZURE_COMPUTER_VISION_KEY=91763b26b4ed446c8f77b982ff4a9ed8,ENVIRONMENT=production,PORT=8080"

# Get the service URL
SERVICE_URL=$(gcloud run services describe bionexus-backend --region=us-central1 --format="value(status.url)")

echo ""
echo "✅ Deployment complete!"
echo "🌐 Your BioNexus API is live at: $SERVICE_URL"
echo "📋 API Documentation: $SERVICE_URL/docs"
echo "📊 Database Stats: $SERVICE_URL/stats"
echo "🔍 Knowledge Graph: $SERVICE_URL/kg/explore"

# Test the deployment
echo ""
echo "🧪 Testing deployment..."
curl -s "$SERVICE_URL/stats" || echo "Service starting up..."

# Frontend deployment to Cloud Run
echo ""
echo "🎨 Deploying frontend to Cloud Run..."
cd ../frontend

# Create environment file with backend URL
echo "NEXT_PUBLIC_API_URL=$SERVICE_URL" > .env.production

# Deploy frontend
gcloud run deploy bionexus-frontend \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --max-instances 5

FRONTEND_URL=$(gcloud run services describe bionexus-frontend --region=us-central1 --format="value(status.url)")

echo ""
echo "🎉 Complete deployment successful!"
echo "🌐 Frontend: $FRONTEND_URL"
echo "🔗 Backend API: $SERVICE_URL"
echo ""
echo "🌍 Custom Domain Setup:"
echo "Configure bionexus.study DNS to point to: $FRONTEND_URL"