# 🚀 **BioNexus - NEXT STEPS**
*Exact steps to get your research platform running perfectly*

## 📋 **STEP 1: Initial Setup**

### Run the Setup Script
```bash
cd "/run/media/CypherKing/Local Disk/BioNexus"
./setup.sh
```

**Choose your setup option:**
- **Option 1**: Local development only (recommended for testing)
- **Option 2**: Local + Azure AI (enhanced features)
- **Option 3**: Full production (cloud deployment)

---

## 🔧 **STEP 2: Configure Database Credentials**

### Edit the .env file
```bash
nano .env
```

**Replace these placeholders with your actual credentials:**

```env
# Required Database Configuration
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_PASSWORD=your_actual_password

MILVUS_HOST=https://your-instance.serverless.cloud.zilliz.com
MILVUS_USER=your_username  
MILVUS_PASSWORD=your_actual_password

# Optional but recommended
OPENAI_API_KEY=sk-your_openai_key
HUGGINGFACE_API_KEY=hf_your_huggingface_key
```

**Where to get these:**
- **Neo4j Aura**: https://console.neo4j.io (you already have this working)
- **Milvus Cloud**: https://cloud.zilliz.com (you already have this working)
- **OpenAI**: https://platform.openai.com/api-keys
- **HuggingFace**: https://huggingface.co/settings/tokens

---

## 🚀 **STEP 3: Start the Application**

### Start Backend (Terminal 1)
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (Terminal 2)
```bash
cd frontend
npm run dev
```

### Access Your Platform
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

---

## 🧪 **STEP 4: Test Core Features**

### Test Knowledge Graph
1. Open http://localhost:3000
2. Navigate to Knowledge Graph section
3. Verify you see nodes and can interact with them
4. Test search within the graph

### Test Search Functionality
1. Use the search bar on the homepage
2. Try queries like "microgravity", "protein synthesis"
3. Verify results appear with multiple data sources
4. Test semantic search with vector similarities

### Test Charts and Analytics
1. Check the dashboard for visualizations
2. Verify charts are displaying data
3. Test interactive elements

---

## 🎯 **STEP 5: Production Deployment (Optional)**

### Prerequisites for Cloud Deployment
1. **Google Cloud Project**: Create at https://console.cloud.google.com
2. **Porkbun Domain**: Your domain bionexus.study
3. **Azure Subscription**: If using Azure AI features

### Deploy to Production
```bash
cd cloud-deployment

# Set up your credentials
echo "PROJECT_ID=your-gcp-project-id" > .env.prod
echo "DOMAIN_NAME=bionexus.study" >> .env.prod
echo "AZURE_SUBSCRIPTION_ID=your-azure-sub-id" >> .env.prod

# Initialize and deploy
terraform init
terraform plan -var-file="terraform.tfvars"
terraform apply
```

---

## � **STEP 6: REQUIRED CREDENTIALS FOR CLOUD SERVICES**

### **🌐 Google Cloud Platform (Required for Production)**

#### **What You Need:**
1. **GCP Project ID**
   - Example: `bionexus-research-2025`
   - Get it: https://console.cloud.google.com → Create/Select Project

#### **How to Get Credentials:**
```bash
# 1. Install Google Cloud CLI
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
gcloud init

# 2. Create new project (or use existing)
gcloud projects create bionexus-research-2025 --name="BioNexus Research"

# 3. Set as default project
gcloud config set project bionexus-research-2025

# 4. Enable billing (required for Cloud Run)
# Go to: https://console.cloud.google.com/billing

# 5. Get your project ID
gcloud config get-value project
```

#### **Required for Terraform:**
```env
# Add to your .env file
GCP_PROJECT_ID=bionexus-research-2025
GCP_REGION=us-central1
```

---

### **🌐 Porkbun Domain (Required for Custom Domain)**

#### **What You Need:**
1. **Domain Name**: `bionexus.study` (you already own this)
2. **Porkbun API Key**
3. **Porkbun Secret Key**

#### **How to Get API Credentials:**
```bash
# 1. Login to Porkbun: https://porkbun.com/account/api
# 2. Enable API Access
# 3. Generate API Key and Secret
```

#### **Required Credentials:**
```env
# Add to your .env file
PORKBUN_API_KEY=pk1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PORKBUN_SECRET_KEY=sk1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DOMAIN_NAME=bionexus.study
```

---

### **☁️ Azure (Optional - For AI Features)**

#### **What You Need:**
1. **Azure Subscription ID**
2. **Azure Resource Group** (will be created automatically)
3. **Service Principal** (for Terraform automation)

#### **How to Get Credentials:**
```bash
# 1. Install Azure CLI
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash

# 2. Login to Azure
az login

# 3. Get your Subscription ID
az account show --query "id" -o tsv

# 4. Create Service Principal for Terraform (optional)
az ad sp create-for-rbac --name "bionexus-terraform" --role="Contributor" --scopes="/subscriptions/YOUR_SUBSCRIPTION_ID"
```

#### **Required Credentials:**
```env
# Add to your .env file
AZURE_SUBSCRIPTION_ID=12345678-1234-1234-1234-123456789012

# Optional: For automated deployment
AZURE_CLIENT_ID=12345678-1234-1234-1234-123456789012
AZURE_CLIENT_SECRET=your_client_secret
AZURE_TENANT_ID=12345678-1234-1234-1234-123456789012
```

---

### **📝 Complete .env File Template**

```env
# ==============================================
# BioNexus Production Environment Configuration
# Domain: bionexus.study
# ==============================================

# DATABASE CONFIGURATION (Already Working)
NEO4J_URI=neo4j+s://e3671855.databases.neo4j.io
NEO4J_PASSWORD=your_neo4j_password
MILVUS_HOST=https://in03-9ec7c214a18d7a5.serverless.aws-eu-central-1.cloud.zilliz.com
MILVUS_USER=db_username
MILVUS_PASSWORD=your_milvus_password

# GOOGLE CLOUD PLATFORM (Required for Production)
GCP_PROJECT_ID=bionexus-research-2025
GCP_REGION=us-central1

# PORKBUN DOMAIN (Required for Custom Domain)
PORKBUN_API_KEY=pk1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
PORKBUN_SECRET_KEY=sk1_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DOMAIN_NAME=bionexus.study

# AZURE AI SERVICES (Optional - Enhanced Features)
AZURE_SUBSCRIPTION_ID=12345678-1234-1234-1234-123456789012
AZURE_TEXT_ENDPOINT=https://bionexus-text-analytics.cognitiveservices.azure.com/
AZURE_TEXT_KEY=your_azure_text_key
AZURE_VISION_ENDPOINT=https://bionexus-computer-vision.cognitiveservices.azure.com/
AZURE_VISION_KEY=your_azure_vision_key

# API KEYS (Optional but Recommended)
OPENAI_API_KEY=sk-your_openai_key
HUGGINGFACE_API_KEY=hf_your_huggingface_key
GOOGLE_MAPS_API_KEY=your_google_maps_key

# SECURITY (Auto-generated)
JWT_SECRET_KEY=your_jwt_secret_key
```

---

### **🎯 STEP-BY-STEP CREDENTIAL SETUP**

#### **Step 6.1: Google Cloud Setup**
```bash
# Create GCP project and get project ID
gcloud projects create bionexus-research-2025
gcloud config set project bionexus-research-2025
echo "GCP_PROJECT_ID=$(gcloud config get-value project)" >> .env
```

#### **Step 6.2: Porkbun API Setup**
```bash
# 1. Go to: https://porkbun.com/account/api
# 2. Enable API access for your account
# 3. Click "Create API Key"
# 4. Copy both API Key and Secret Key
# 5. Add to .env file:
echo "PORKBUN_API_KEY=pk1_your_actual_key" >> .env
echo "PORKBUN_SECRET_KEY=sk1_your_actual_secret" >> .env
```

#### **Step 6.3: Azure Setup (Optional)**
```bash
# Get subscription ID and add to .env
AZURE_SUB_ID=$(az account show --query "id" -o tsv)
echo "AZURE_SUBSCRIPTION_ID=$AZURE_SUB_ID" >> .env
```

---

### **⚡ AUTOMATED CREDENTIAL SETUP**

Run this command to set up all services at once:
```bash
# This will prompt you for each credential
./setup.sh --production
```

The script will:
1. ✅ Create GCP project and enable APIs
2. ✅ Validate Porkbun domain access
3. ✅ Set up Azure AI services
4. ✅ Generate all required configuration
5. ✅ Test all connections

---

## �🔍 **STEP 7: Verification Checklist**

### ✅ **Local Development Checklist**
- [ ] Backend starts without errors on port 8000
- [ ] Frontend loads successfully on port 3000
- [ ] Knowledge graph displays with your Neo4j data
- [ ] Search returns results from both Neo4j and Milvus
- [ ] Charts and visualizations work
- [ ] No console errors in browser

### ✅ **Azure AI Integration (if enabled)**
- [ ] Azure services created successfully
- [ ] Text analytics endpoints respond
- [ ] Enhanced biomedical NER working
- [ ] Image analysis functional
- [ ] No Azure credential errors

### ✅ **Production Deployment (if chosen)**
- [ ] Terraform deployment successful
- [ ] Domain bionexus.study resolves
- [ ] SSL certificates active
- [ ] API endpoints accessible via domain
- [ ] Auto-scaling working

---

## 🐛 **TROUBLESHOOTING**

### Backend Won't Start
```bash
# Check Python environment
cd backend
source venv/bin/activate
python --version  # Should be 3.8+

# Check dependencies
pip list | grep fastapi
pip list | grep neo4j

# Check environment variables
python -c "import os; print('NEO4J_URI:', os.getenv('NEO4J_URI'))"
```

### Frontend Build Fails
```bash
cd frontend
npm --version  # Should be 8+
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run build
```

### Database Connection Issues
```bash
# Test Neo4j connection
cd backend
source venv/bin/activate
python -c "
from app.services.neo4j_client import neo4j_client
print('Testing Neo4j...')
result = neo4j_client.execute_query('MATCH (n) RETURN count(n) as count')
print(f'Node count: {result[0][\"count\"]}')
"

# Test Milvus connection
python -c "
from app.services.milvus_client import milvus_client
print('Testing Milvus...')
collections = milvus_client.list_collections()
print(f'Collections: {collections}')
"
```

---

## 🎉 **SUCCESS INDICATORS**

### Your BioNexus platform is working perfectly when:

1. **✅ Homepage loads** with search bar and navigation
2. **✅ Knowledge Graph** displays interactive nodes from your Neo4j data
3. **✅ Search functionality** returns results from multiple sources
4. **✅ Analytics dashboard** shows charts and metrics
5. **✅ API documentation** is accessible at /docs
6. **✅ No console errors** in browser developer tools
7. **✅ Backend health check** passes at /health

### Performance Indicators:
- Search queries respond within 2-3 seconds
- Knowledge graph renders smoothly with 130+ nodes
- Vector search provides relevant semantic results
- Charts update dynamically with real data

---

## 🌟 **NEXT LEVEL FEATURES**

Once your platform is running perfectly, consider adding:

### Enhanced Features
- **User Authentication**: Add login/logout functionality
- **Real-time Collaboration**: Multi-user research sessions
- **Advanced Analytics**: Research trend analysis
- **Export Capabilities**: PDF reports, data dumps
- **Mobile App**: React Native companion app

### AI Enhancements (with Azure)
- **Automated Paper Analysis**: Process new research papers
- **Smart Recommendations**: ML-powered research suggestions
- **Natural Language Queries**: Ask questions in plain English
- **Research Assistant**: AI-powered research guidance

---

## 🆘 **GET HELP**

### If you encounter issues:
1. **Check the logs**: Backend terminal shows detailed error messages
2. **Verify credentials**: Ensure all .env variables are correct
3. **Test connections**: Use the troubleshooting commands above
4. **Check prerequisites**: Python 3.8+, Node.js 18+, npm 8+

### Common Solutions:
- **Port conflicts**: Change ports if 3000/8000 are in use
- **Permission errors**: Ensure script is executable (`chmod +x setup.sh`)
- **Network issues**: Check firewall settings for cloud services
- **Version conflicts**: Use the exact versions specified

---

## 🎯 **YOUR MISSION**

**Follow these steps in order:**
1. ✅ Run `./setup.sh`
2. ✅ Configure `.env` with your credentials  
3. ✅ Start backend and frontend
4. ✅ Test all core features
5. ✅ Verify everything works perfectly
6. 🚀 Deploy to production (optional)

**Your BioNexus research platform will be fully operational and ready to serve researchers worldwide!**