# 🚀 BioNexus Next Steps - Complete Setup Guide

## Overview
Your BioNexus platform is a **read-only application** that consumes pre-processed research data from cloud services. The backend queries existing data from Neo4j Aura (knowledge graph) and Milvus Cloud (vector embeddings) without performing data processing. 

**Prerequisites**: Data must be pre-processed and loaded into Neo4j Aura and Milvus Cloud before running this application.

---

## ✅ Step 1: Set Up Cloud Services

### 1.1 Neo4j Aura (Knowledge Graph Database) - **REQUIRED**
1. Go to [https://neo4j.com/aura/](https://neo4j.com/aura/)
2. Sign up for free account
3. Create a new database (Free tier available)
4. **Save the credentials**:
   - Connection URI (format: `neo4j+s://xxxxx.databases.neo4j.io`)
   - Username: `neo4j`
   - Password: (you set this)

### 1.2 Milvus Cloud (Vector Database) - **REQUIRED**
1. Go to [https://zilliz.com/cloud](https://zilliz.com/cloud)
2. Sign up for free account
3. Create a new cluster (Free tier: 1GB storage)
4. **Save the credentials**:
   - Cluster endpoint (format: `xxxxx.milvusdb.io`)
   - Username and Password (you create these)

### 1.3 Google Cloud Platform (Storage & Infrastructure) - **REQUIRED**
1. Go to [https://console.cloud.google.com/](https://console.cloud.google.com/)
2. Create a new project (or use existing)
3. Enable Cloud Storage API
4. Create a storage bucket (name: `bionexus-documents-[your-suffix]`)
5. Create service account with Storage Admin role
6. Download service account JSON key file
7. **Save the details**:
   - Project ID
   - Bucket name
   - Service account JSON file path

### 1.4 OpenAI API (AI Services) - **REQUIRED**
1. Go to [https://platform.openai.com/](https://platform.openai.com/)
2. Create account and add payment method
3. Generate API key
4. **Save the API key**: `sk-proj-xxxxx`

---

## ✅ Step 2: Configure Environment

### 2.1 Create Environment File
```bash
cd /run/media/CypherKing/Local\ Disk/BioNexus
cp .env.example .env
```

### 2.2 Edit `.env` File with Your Credentials
```bash
nano .env
```

**Add your actual credentials**:
```env
# Neo4j Aura (REQUIRED)
NEO4J_URI=neo4j+s://your-actual-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-actual-neo4j-password
NEO4J_DATABASE=neo4j

# Milvus Cloud (REQUIRED)
MILVUS_HOST=your-actual-endpoint.milvusdb.io
MILVUS_PORT=19530
MILVUS_USER=your-actual-milvus-username
MILVUS_PASSWORD=your-actual-milvus-password
MILVUS_SECURE=true
MILVUS_COLLECTION_NAME=bionexus_embeddings

# Google Cloud Storage (REQUIRED)
GCS_BUCKET_NAME=your-actual-bucket-name
GCS_PROJECT_ID=your-actual-gcp-project-id
GCS_CREDENTIALS_PATH=/app/gcp-key.json

# OpenAI API (REQUIRED)
OPENAI_API_KEY=sk-proj-your-actual-openai-key

# Hugging Face (RECOMMENDED)
HUGGINGFACE_API_KEY=hf_your-actual-huggingface-token

# Optional Services (can be added later)
METEOMATICS_USERNAME=
METEOMATICS_PASSWORD=
AZURE_COGNITIVE_KEY=
MIRO_API_KEY=
GOOGLE_MAPS_API_KEY=

# Application Settings
ENVIRONMENT=production
CLOUD_ENVIRONMENT=gcp
DEBUG=false
LOG_LEVEL=INFO
```

### 2.3 Place Google Cloud Credentials
```bash
# Copy your downloaded service account JSON file
cp /path/to/your-gcp-service-account.json ./gcp-key.json
```

---

## ✅ Step 3: Test Cloud Connectivity

### 3.1 Run Connection Tests
```bash
chmod +x ./test-cloud-services.sh
./test-cloud-services.sh
```

**Expected output**: All services should show ✅ CONNECTED

If any service shows ❌ FAILED:
- Double-check credentials in `.env` file
- Verify service is created and running in cloud console
- Check network connectivity

---

## ✅ Step 4: Deploy Application

### 4.1 Local Deployment (Recommended for testing)
```bash
# Build and start containers
docker-compose up --build -d

# Check status
docker-compose ps

# View logs if needed
docker-compose logs backend
docker-compose logs frontend
```

### 4.2 Access Your Application
- **Frontend**: [http://localhost:3000](http://localhost:3000)
- **API**: [http://localhost:8000](http://localhost:8000)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)

### 4.3 Production Cloud Deployment (Optional)
```bash
# Deploy to Google Cloud Platform
./cloud-deployment/deploy.sh your-gcp-project-id us-central1 yourdomain.com
```

---

## ✅ Step 5: Verify Pre-Processed Data

### 5.1 Check Neo4j Aura Data
- Ensure your Neo4j database contains:
  - `Publication` nodes (research papers)
  - `Page` nodes (document pages) 
  - `Entity` nodes (biomedical entities)
  - `CONTAINS`, `MENTIONS`, `RELATES_TO` relationships

### 5.2 Check Milvus Cloud Data
- Verify your Milvus collection contains:
  - Document page embeddings (ColPali/multimodal)
  - Proper metadata (pub_id, page_id, etc.)
  - Vector dimensions matching your embedding model

### 5.3 Test Data Connectivity
```bash
# Test Neo4j connection and data
curl -X GET "http://localhost:8000/health"

# Test vector search functionality  
curl -X GET "http://localhost:8000/search/stats"
```

---

## ✅ Step 6: Verify Everything Works

### 6.1 Test Core Features
1. **Document Upload**: Upload a test PDF
2. **Search**: Perform semantic search queries
3. **Knowledge Graph**: View entity relationships
4. **RAG System**: Ask questions about uploaded content

### 6.2 Check System Health
```bash
# API health check
curl http://localhost:8000/health

# Check service statistics  
curl http://localhost:8000/kg/statistics
```

---

## 🎯 Success Criteria

Your BioNexus platform is **fully operational** when:

- ✅ All cloud services connect successfully
- ✅ Containers start without errors
- ✅ Frontend loads at localhost:3000
- ✅ API responds at localhost:8000
- ✅ Document upload and processing works
- ✅ Semantic search returns results
- ✅ Knowledge graph visualizes data

---

## 🆘 Troubleshooting

### Common Issues:

**Connection Errors**:
- Verify `.env` credentials are correct
- Check cloud service status in their consoles
- Ensure network connectivity

**Container Issues**:
```bash
# Restart services
docker-compose restart

# Rebuild if code changes
docker-compose up --build -d

# View detailed logs
docker-compose logs -f backend
```

**Performance Issues**:
- Increase Docker memory allocation (8GB+ recommended)
- Use SSD storage for better I/O performance
- Monitor resource usage: `docker stats`

---

## 📞 Support

If you encounter issues:
1. Check logs: `docker-compose logs`
2. Verify credentials in cloud service consoles
3. Test individual service connections
4. Review API documentation at `/docs` endpoint

---

## 🎉 Final Result

Once complete, you'll have:
- **Scalable cloud infrastructure** handling millions of documents
- **Advanced AI-powered search** across biomedical literature  
- **Interactive knowledge graph** showing entity relationships
- **Production-ready platform** for real research workflows

**Your BioNexus platform will be ready for serious biomedical research! 🧬🔬**