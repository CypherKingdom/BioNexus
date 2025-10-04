#!/bin/bash

# BioNexus Cloud Deployment Script
# This script automates the complete deployment of BioNexus to Google Cloud Platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID=${1:-"bionexus-production"}
REGION=${2:-"us-central1"}
DOMAIN_NAME=${3:-"bionexus.space"}

echo -e "${BLUE}🚀 BioNexus Cloud Deployment Starting...${NC}"
echo -e "${BLUE}Project ID: ${PROJECT_ID}${NC}"
echo -e "${BLUE}Region: ${REGION}${NC}"
echo -e "${BLUE}Domain: ${DOMAIN_NAME}${NC}"

# Check prerequisites
echo -e "\n${YELLOW}📋 Checking prerequisites...${NC}"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}❌ gcloud CLI is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if terraform is installed
if ! command -v terraform &> /dev/null; then
    echo -e "${RED}❌ Terraform is not installed. Please install it first.${NC}"
    exit 1
fi

# Check if docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install it first.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Set up Google Cloud project
echo -e "\n${YELLOW}🏗️ Setting up Google Cloud project...${NC}"

# Set project
gcloud config set project $PROJECT_ID

# Enable required APIs
echo -e "${YELLOW}🔧 Enabling required APIs...${NC}"
gcloud services enable \
    run.googleapis.com \
    cloudbuild.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    bigquery.googleapis.com \
    monitoring.googleapis.com \
    logging.googleapis.com

echo -e "${GREEN}✅ APIs enabled${NC}"

# Create necessary secrets
echo -e "\n${YELLOW}🔐 Creating Secret Manager secrets...${NC}"

# Function to create secret if it doesn't exist
create_secret_if_not_exists() {
    local secret_name=$1
    local secret_value=$2
    
    if ! gcloud secrets describe $secret_name &> /dev/null; then
        echo "Creating secret: $secret_name"
        echo -n "$secret_value" | gcloud secrets create $secret_name --data-file=-
    else
        echo "Secret $secret_name already exists, updating..."
        echo -n "$secret_value" | gcloud secrets versions add $secret_name --data-file=-
    fi
}

# Create secrets (you'll need to replace these with actual values)
echo -e "${YELLOW}🔐 Creating cloud service secrets...${NC}"
echo "Please ensure you have the following credentials ready:"
echo "- Neo4j Aura connection details"
echo "- Milvus Cloud credentials"  
echo "- OpenAI API key"
echo "- Google Maps API key"
echo ""

# Neo4j Aura secrets
create_secret_if_not_exists "neo4j-uri" "neo4j+s://your-aura-instance.databases.neo4j.io"
create_secret_if_not_exists "neo4j-password" "your-neo4j-aura-password"

# Milvus Cloud secrets
create_secret_if_not_exists "milvus-host" "your-cluster.milvusdb.io"
create_secret_if_not_exists "milvus-user" "your-milvus-username"
create_secret_if_not_exists "milvus-password" "your-milvus-password"

# API Keys
create_secret_if_not_exists "openai-api-key" "sk-proj-your-openai-api-key"
create_secret_if_not_exists "huggingface-api-key" "hf_your-huggingface-token"
create_secret_if_not_exists "google-maps-api-key" "your-google-maps-api-key"

# External integrations (optional)
create_secret_if_not_exists "meteomatics-username" "your-meteomatics-username"
create_secret_if_not_exists "meteomatics-password" "your-meteomatics-password"
create_secret_if_not_exists "miro-api-key" "your-miro-api-key"
create_secret_if_not_exists "miro-client-id" "your-miro-client-id"

# Security
create_secret_if_not_exists "jwt-secret-key" "$(openssl rand -base64 32)"

echo -e "${GREEN}✅ Secrets created${NC}"

# Deploy infrastructure with Terraform
echo -e "\n${YELLOW}🏗️ Deploying infrastructure with Terraform...${NC}"

cd cloud-deployment/terraform

# Initialize Terraform
terraform init

# Plan deployment
terraform plan \
    -var="project_id=$PROJECT_ID" \
    -var="region=$REGION" \
    -var="domain_name=$DOMAIN_NAME"

# Apply deployment
terraform apply -auto-approve \
    -var="project_id=$PROJECT_ID" \
    -var="region=$REGION" \
    -var="domain_name=$DOMAIN_NAME"

cd ../..

echo -e "${GREEN}✅ Infrastructure deployed${NC}"

# Build and deploy application
echo -e "\n${YELLOW}🔨 Building and deploying application...${NC}"

# Configure Docker for GCR
gcloud auth configure-docker

# Submit build to Cloud Build
gcloud builds submit . --config=cloud-deployment/cloudbuild.yaml

echo -e "${GREEN}✅ Application deployed${NC}"

# Set up monitoring and alerting
echo -e "\n${YELLOW}📊 Setting up monitoring...${NC}"

# Create BigQuery dataset and tables (done by Terraform)
echo -e "${GREEN}✅ Monitoring configured${NC}"

# Get deployment URLs
echo -e "\n${YELLOW}🌐 Getting deployment information...${NC}"

BACKEND_URL=$(gcloud run services describe bionexus-backend --region=$REGION --format="value(status.url)")
FRONTEND_URL=$(gcloud run services describe bionexus-frontend --region=$REGION --format="value(status.url)")

echo -e "\n${GREEN}🎉 Deployment completed successfully!${NC}"
echo -e "\n${BLUE}📋 Deployment Information:${NC}"
echo -e "Frontend URL: $FRONTEND_URL"
echo -e "Backend URL: $BACKEND_URL"
echo -e "API Documentation: $BACKEND_URL/docs"

echo -e "\n${YELLOW}🔧 Next Steps:${NC}"
echo -e "1. Update your domain DNS settings:"
echo -e "   - Add CNAME record: app.$DOMAIN_NAME -> ghs.googlehosted.com"
echo -e "   - Add CNAME record: api.$DOMAIN_NAME -> ghs.googlehosted.com"
echo -e ""
echo -e "2. Configure domain mapping in Cloud Run:"
echo -e "   gcloud run domain-mappings create --service=bionexus-frontend --domain=app.$DOMAIN_NAME --region=$REGION"
echo -e "   gcloud run domain-mappings create --service=bionexus-backend --domain=api.$DOMAIN_NAME --region=$REGION"
echo -e ""
echo -e "3. Update your frontend environment variables to use the custom domain"
echo -e ""
echo -e "4. Set up your external API integrations with the actual API keys"

echo -e "\n${GREEN}✅ BioNexus is now running in the cloud! 🚀${NC}"