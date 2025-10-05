#!/bin/bash
# 🚀 BioNexus Complete Setup & Test Script
# Domain: bionexus.study
# This is the ONLY setup script you need!

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 BioNexus Complete Setup & Test${NC}"
echo -e "${BLUE}Domain: bionexus.study${NC}"
echo "==========================================="
echo ""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to prompt for input
prompt_input() {
    local prompt="$1"
    local var_name="$2"
    local default="$3"
    
    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " input
        if [ -z "$input" ]; then
            input="$default"
        fi
    else
        read -p "$prompt: " input
    fi
    
    eval "$var_name='$input'"
}

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check Python
if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.8+${NC}"
    exit 1
else
    echo -e "${GREEN}✅ Python 3 found${NC}"
fi

# Check pip
if ! command_exists pip3; then
    echo -e "${RED}❌ pip3 not found. Please install pip${NC}"
    exit 1
else
    echo -e "${GREEN}✅ pip3 found${NC}"
fi

# Check Node.js
if ! command_exists node; then
    echo -e "${YELLOW}⚠️  Node.js not found. Installing...${NC}"
    curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
    sudo apt-get install -y nodejs
else
    echo -e "${GREEN}✅ Node.js found${NC}"
fi

# Check npm
if ! command_exists npm; then
    echo -e "${RED}❌ npm not found. Please install npm${NC}"
    exit 1
else
    echo -e "${GREEN}✅ npm found${NC}"
fi

# Setup options
echo ""
echo -e "${BLUE}🎯 Setup Options:${NC}"
echo "1. Local Development Only (Neo4j + Milvus + Basic Features)"
echo "2. Local + Azure AI Integration (Enhanced Features)"
echo "3. Full Production Setup (GCP + Azure + Domain)"
echo ""

prompt_input "Choose setup option (1-3)" SETUP_OPTION "1"

# Navigate to project directory
PROJECT_DIR="/run/media/CypherKing/Local Disk/BioNexus"
cd "$PROJECT_DIR"

# Setup backend
echo ""
echo -e "${YELLOW}📦 Setting up Backend...${NC}"
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Azure dependencies if option 2 or 3
if [ "$SETUP_OPTION" = "2" ] || [ "$SETUP_OPTION" = "3" ]; then
    echo "Installing Azure AI dependencies..."
    pip install azure-ai-textanalytics azure-cognitiveservices-vision-computervision azure-core
fi

# Setup frontend
echo ""
echo -e "${YELLOW}📦 Setting up Frontend...${NC}"
cd ../frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

# Build frontend
echo "Building frontend..."
npm run build

# Setup environment variables
echo ""
echo -e "${YELLOW}🔧 Setting up Environment...${NC}"
cd ..

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cat > .env << EOF
# BioNexus Environment Configuration
# Domain: bionexus.study

# Database Configuration (Required)
NEO4J_URI=your_neo4j_aura_uri
NEO4J_PASSWORD=your_neo4j_password
MILVUS_HOST=your_milvus_host
MILVUS_USER=your_milvus_user
MILVUS_PASSWORD=your_milvus_password

# API Keys (Optional but recommended)
OPENAI_API_KEY=your_openai_key
HUGGINGFACE_API_KEY=your_huggingface_key

# Azure AI (Only if you chose option 2 or 3)
# AZURE_TEXT_ENDPOINT=your_azure_text_endpoint
# AZURE_TEXT_KEY=your_azure_text_key
# AZURE_VISION_ENDPOINT=your_azure_vision_endpoint
# AZURE_VISION_KEY=your_azure_vision_key

# Production (Only if you chose option 3)
# GCP_PROJECT_ID=your_gcp_project
# AZURE_SUBSCRIPTION_ID=your_azure_subscription

EOF
    echo -e "${GREEN}✅ .env file created${NC}"
    echo -e "${YELLOW}⚠️  Please edit .env file with your actual credentials${NC}"
else
    echo -e "${GREEN}✅ .env file already exists${NC}"
fi

# Azure setup if selected
if [ "$SETUP_OPTION" = "2" ] || [ "$SETUP_OPTION" = "3" ]; then
    echo ""
    echo -e "${YELLOW}☁️  Azure AI Setup...${NC}"
    
    # Check if Azure CLI is installed
    if ! command_exists az; then
        echo "Installing Azure CLI..."
        curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
    fi
    
    # Check if user is logged in
    if ! az account show &> /dev/null; then
        echo "Please login to Azure..."
        az login
    fi
    
    # Azure resource creation
    RESOURCE_GROUP="bionexus-ai-services"
    LOCATION="eastus"
    TEXT_ANALYTICS_NAME="bionexus-text-analytics"
    COMPUTER_VISION_NAME="bionexus-computer-vision"
    
    echo "Creating Azure resources..."
    
    # Create resource group
    az group create --name "$RESOURCE_GROUP" --location "$LOCATION" --output none
    
    # Create services
    az cognitiveservices account create \
        --name "$TEXT_ANALYTICS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --kind "TextAnalytics" \
        --sku "S" \
        --location "$LOCATION" \
        --yes --output none
    
    az cognitiveservices account create \
        --name "$COMPUTER_VISION_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --kind "ComputerVision" \
        --sku "S1" \
        --location "$LOCATION" \
        --yes --output none
    
    # Get credentials
    AZURE_TEXT_ENDPOINT=$(az cognitiveservices account show \
        --name "$TEXT_ANALYTICS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "properties.endpoint" -o tsv)
    
    AZURE_TEXT_KEY=$(az cognitiveservices account keys list \
        --name "$TEXT_ANALYTICS_NAME" \
        --resource-group "$RESOURCE_GROUP" \
        --query "key1" -o tsv)
    
    # Update .env file with Azure credentials
    sed -i "s|# AZURE_TEXT_ENDPOINT=.*|AZURE_TEXT_ENDPOINT=$AZURE_TEXT_ENDPOINT|" .env
    sed -i "s|# AZURE_TEXT_KEY=.*|AZURE_TEXT_KEY=$AZURE_TEXT_KEY|" .env
    
    echo -e "${GREEN}✅ Azure AI services configured${NC}"
fi

# Test the setup
echo ""
echo -e "${YELLOW}🧪 Testing Setup...${NC}"

# Test backend
echo "Testing backend dependencies..."
cd backend
source venv/bin/activate

# Simple import test
python3 -c "
import sys
try:
    from app.main import app
    from app.services.neo4j_client import neo4j_client
    from app.services.milvus_client import milvus_client
    print('✅ Backend imports successful')
except ImportError as e:
    print(f'❌ Backend import error: {e}')
    sys.exit(1)
"

# Test frontend build
echo "Testing frontend build..."
cd ../frontend
if [ -d "out" ] || [ -d ".next" ]; then
    echo -e "${GREEN}✅ Frontend build successful${NC}"
else
    echo -e "${RED}❌ Frontend build failed${NC}"
fi

cd ..

# Final summary
echo ""
echo -e "${GREEN}🎉 BioNexus Setup Complete!${NC}"
echo "=========================================="

echo ""
echo -e "${BLUE}📋 What's Ready:${NC}"
echo "✅ Backend API with FastAPI"
echo "✅ Frontend with Next.js"
echo "✅ Knowledge Graph visualization"
echo "✅ Search functionality"
echo "✅ Chart components"

if [ "$SETUP_OPTION" = "2" ] || [ "$SETUP_OPTION" = "3" ]; then
    echo "✅ Azure AI integration"
fi

echo ""
echo -e "${BLUE}🚀 Next Steps:${NC}"
echo "1. Edit .env file with your database credentials"
echo "2. Start backend: cd backend && source venv/bin/activate && python -m uvicorn app.main:app --reload"
echo "3. Start frontend: cd frontend && npm run dev"
echo "4. Open http://localhost:3000 in your browser"

if [ "$SETUP_OPTION" = "3" ]; then
    echo "5. For production: Follow NEXT_STEPS.md for cloud deployment"
fi

echo ""
echo -e "${YELLOW}⚠️  Important:${NC}"
echo "- Update .env with your actual Neo4j and Milvus credentials"
echo "- Never commit .env file to version control"
echo "- Monitor Azure usage if enabled"

echo ""
echo -e "${GREEN}Happy researching with BioNexus! 🧬${NC}"