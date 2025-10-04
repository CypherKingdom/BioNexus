# ☁️ BioNexus Cloud Setup Guide

This guide will help you deploy BioNexus with all cloud services - Neo4j Aura, Milvus Cloud, and Google Cloud Platform.

## 🎯 Cloud Services Required

### 1. Neo4j Aura (Knowledge Graph Database)
- **Service**: Neo4j Aura Free/Professional
- **URL**: https://neo4j.com/aura/
- **What you'll get**: 
  - Connection URI: `neo4j+s://xxxxx.databases.neo4j.io`
  - Username: `neo4j` 
  - Password: Generated password

### 2. Milvus Cloud (Vector Database)
- **Service**: Zilliz Cloud (Managed Milvus)
- **URL**: https://zilliz.com/cloud
- **What you'll get**:
  - Host endpoint: `xxx-xxx.milvusdb.io`
  - Port: `19530`
  - Username & Password

### 3. Google Cloud Platform (Infrastructure)
- **Required Services**:
  - Cloud Run (Application hosting)
  - Cloud Storage (Document storage)
  - Secret Manager (API key management)
  - BigQuery (Analytics)

## 📋 Step-by-Step Setup

### Step 1: Set Up Neo4j Aura

1. **Create Neo4j Aura Account**
   ```bash
   # Go to https://neo4j.com/aura/
   # Sign up for free account
   # Create new instance:
   # - Instance Type: AuraDB Free (or Professional)
   # - Region: Choose closest to your users
   # - Database: Neo4j 5.x
   ```

2. **Save Connection Details**
   ```bash
   # You'll receive:
   NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
   NEO4J_USER=neo4j
   NEO4J_PASSWORD=generated-password-here
   ```

3. **Test Connection**
   ```bash
   # Install Neo4j Desktop or use browser interface
   # Connect with your credentials to verify
   ```

### Step 2: Set Up Milvus Cloud (Zilliz)

1. **Create Zilliz Cloud Account**
   ```bash
   # Go to https://zilliz.com/cloud
   # Sign up and verify email
   # Create new cluster:
   # - Cluster Type: Starter (free tier) or Standard
   # - Cloud Provider: AWS/GCP (choose same region as your app)
   # - Region: us-east-1 or similar
   ```

2. **Configure Cluster**
   ```bash
   # After cluster creation, you'll get:
   MILVUS_HOST=xxx-xxx.milvusdb.io
   MILVUS_PORT=19530
   MILVUS_USER=your-username
   MILVUS_PASSWORD=your-password
   MILVUS_SECURE=true
   ```

3. **Test Connection**
   ```bash
   pip install pymilvus
   python -c "
   from pymilvus import connections
   connections.connect(
       host='your-host.milvusdb.io',
       port='19530', 
       user='your-user',
       password='your-password',
       secure=True
   )
   print('Milvus connection successful!')
   "
   ```

### Step 3: Set Up Google Cloud Platform

1. **Create GCP Project**
   ```bash
   # Go to https://console.cloud.google.com/
   # Create new project: bionexus-production
   # Enable billing for the project
   gcloud config set project bionexus-production
   ```

2. **Enable Required APIs**
   ```bash
   gcloud services enable \
     run.googleapis.com \
     storage.googleapis.com \
     secretmanager.googleapis.com \
     bigquery.googleapis.com \
     cloudbuild.googleapis.com
   ```

3. **Create Service Account**
   ```bash
   gcloud iam service-accounts create bionexus-service \
     --description="BioNexus application service account" \
     --display-name="BioNexus Service Account"
   
   # Download key file
   gcloud iam service-accounts keys create gcp-key.json \
     --iam-account=bionexus-service@bionexus-production.iam.gserviceaccount.com
   ```

### Step 4: Configure API Keys

1. **OpenAI API (Required for RAG)**
   ```bash
   # Go to https://platform.openai.com/api-keys
   # Create new secret key
   OPENAI_API_KEY=sk-proj-xxxxx
   ```

2. **Hugging Face API (Required for ML Models)**
   ```bash
   # Go to https://huggingface.co/settings/tokens
   # Create new token with read access
   HUGGINGFACE_API_KEY=hf_xxxxx
   ```

3. **Google Maps API (Frontend)**
   ```bash
   # Go to https://console.cloud.google.com/apis/credentials
   # Create API key and restrict to Maps JavaScript API
   GOOGLE_MAPS_API_KEY=AIzaSyxxxxx
   ```

4. **Optional External APIs**
   ```bash
   # Meteomatics Weather API
   METEOMATICS_USERNAME=your-username
   METEOMATICS_PASSWORD=your-password
   
   # Azure Cognitive Services
   AZURE_COGNITIVE_KEY=your-azure-key
   
   # Miro Collaboration
   MIRO_API_KEY=your-miro-key
   MIRO_CLIENT_ID=your-miro-client-id
   ```

### Step 5: Deploy to Cloud

1. **Create Environment File**
   ```bash
   # Copy and customize the environment template
   cp .env.example .env
   
   # Edit .env with all your cloud credentials:
   nano .env
   ```

2. **Deploy with Terraform**
   ```bash
   cd cloud-deployment/terraform
   
   # Initialize Terraform
   terraform init
   
   # Plan deployment
   terraform plan \
     -var="project_id=bionexus-production" \
     -var="region=us-central1" \
     -var="domain_name=yourdomain.com"
   
   # Apply deployment
   terraform apply -auto-approve
   ```

3. **Deploy Application**
   ```bash
   # Run the automated deployment script
   ./cloud-deployment/deploy.sh bionexus-production us-central1 yourdomain.com
   ```

## 🔐 Required Environment Variables

Create a `.env` file with these values:

```bash
# Neo4j Aura (REQUIRED)
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-aura-password

# Milvus Cloud (REQUIRED)  
MILVUS_HOST=your-cluster.milvusdb.io
MILVUS_PORT=19530
MILVUS_USER=your-milvus-username
MILVUS_PASSWORD=your-milvus-password
MILVUS_SECURE=true

# Google Cloud (REQUIRED)
GCS_BUCKET_NAME=bionexus-documents
GCS_PROJECT_ID=bionexus-production
GOOGLE_APPLICATION_CREDENTIALS=./gcp-key.json

# API Keys (REQUIRED)
OPENAI_API_KEY=sk-proj-xxxxx
HUGGINGFACE_API_KEY=hf_xxxxx
GOOGLE_MAPS_API_KEY=AIzaSyxxxxx

# Application Settings
ENVIRONMENT=production
CLOUD_ENVIRONMENT=gcp
NEXT_PUBLIC_API_URL=https://api.yourdomain.com

# Optional External APIs
METEOMATICS_USERNAME=your-username
METEOMATICS_PASSWORD=your-password
AZURE_COGNITIVE_KEY=your-azure-key
MIRO_API_KEY=your-miro-key
```

## 🚀 Testing the Deployment

### 1. Test Individual Services

```bash
# Test Neo4j Aura connection
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('neo4j+s://xxx.databases.neo4j.io', auth=('neo4j', 'password'))
with driver.session() as session:
    result = session.run('RETURN 1 as test')
    print('Neo4j Aura:', result.single()['test'])
driver.close()
"

# Test Milvus Cloud connection  
python -c "
from pymilvus import connections
connections.connect(host='xxx.milvusdb.io', port='19530', user='user', password='pass', secure=True)
print('Milvus Cloud: Connected successfully')
"

# Test Google Cloud Storage
python -c "
from google.cloud import storage
client = storage.Client(project='bionexus-production')
bucket = client.bucket('bionexus-documents')
print('GCS Bucket:', bucket.name)
"
```

### 2. Test Full Application

```bash
# Test backend health
curl https://api.yourdomain.com/health

# Test frontend
curl https://app.yourdomain.com

# Test API documentation
open https://api.yourdomain.com/docs
```

## 💰 Cost Estimates

### Monthly Costs (USD)

| Service | Free Tier | Paid Tier |
|---------|-----------|-----------|
| Neo4j Aura | Free (50k nodes) | $65/month (starter) |
| Milvus Cloud | Free (1M vectors) | $20/month (starter) |
| Google Cloud Run | $0-50 | $50-200 |
| Google Cloud Storage | $5-25 | $25-100 |
| OpenAI API | $20-100 | $100-500 |
| **Total** | **$25-175** | **$260-965** |

## 🔧 Maintenance & Monitoring

### 1. Health Monitoring

```bash
# Monitor application health
gcloud run services list --region=us-central1

# Check logs
gcloud logs tail projects/bionexus-production/logs/stdout --limit=100

# Monitor costs
gcloud billing budgets list
```

### 2. Backup Strategies

```bash
# Neo4j Aura has automatic backups
# Milvus Cloud has backup features
# Google Cloud Storage has versioning enabled

# Manual backup commands available in admin interface
```

## 🚨 Troubleshooting

### Common Issues

1. **Neo4j Connection Timeout**
   ```bash
   # Check firewall settings
   # Verify URI format: neo4j+s://xxx.databases.neo4j.io
   # Ensure password is correct
   ```

2. **Milvus Authentication Failed**
   ```bash
   # Verify credentials in Zilliz console
   # Check cluster status (should be running)
   # Ensure secure=True for cloud connections
   ```

3. **GCP Permission Errors**
   ```bash
   # Verify service account permissions
   # Check IAM roles are assigned correctly
   # Ensure billing is enabled
   ```

## 🎯 Next Steps

1. **Configure Domain**: Set up custom domain with SSL certificates
2. **Set up CI/CD**: Automate deployments with GitHub Actions  
3. **Monitor Performance**: Set up alerts and dashboards
4. **Scale Resources**: Monitor usage and scale as needed
5. **Data Migration**: Import your real research data

---

**🚀 Your BioNexus platform is now fully cloud-enabled and ready for production use!**

For support, check the main documentation or create an issue in the repository.