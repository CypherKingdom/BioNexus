#!/bin/bash

echo "🚀 Deploying BioNexus to Google Cloud..."

# Set the correct PATH for gcloud
export PATH="$PATH:/run/media/CypherKing/Local Disk/BioNexus/google-cloud-sdk/bin"

# Set project
echo "📋 Setting GCP project..."
gcloud config set project coral-field-474212-d2

# Enable required APIs
echo "📡 Enabling required APIs..."
gcloud services enable appengine.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# Deploy backend to App Engine
echo "🏗️ Deploying backend to Google App Engine..."
cd backend
cp requirements-prod.txt requirements.txt
gcloud app deploy app.yaml --quiet

# Get backend URL
BACKEND_URL="https://coral-field-474212-d2.uc.r.appspot.com"
echo "✅ Backend deployed at: $BACKEND_URL"

# Build and deploy frontend
echo "🎨 Building frontend..."
cd ../frontend

# Create production environment file
echo "NEXT_PUBLIC_API_URL=$BACKEND_URL" > .env.production

# Build the frontend
npm run build

# Deploy frontend to a separate service
echo "🌐 Deploying frontend..."
cat > app.yaml << EOF
runtime: nodejs18

handlers:
- url: /.*
  static_files: out/\1/index.html
  upload: out/.*/index.html

- url: /.*
  static_files: out/\1
  upload: out/.*

automatic_scaling:
  min_instances: 1
  max_instances: 5
EOF

gcloud app deploy app.yaml --quiet

echo "🎉 Deployment complete!"
echo "🌐 Your website is now live at: https://coral-field-474212-d2.uc.r.appspot.com"
echo ""
echo "🔗 Next steps:"
echo "1. Configure custom domain (bionexus.study) in Google Cloud Console"
echo "2. Update DNS records at Porkbun to point to your App Engine URL"
echo "3. Test all functionality at the live URL"