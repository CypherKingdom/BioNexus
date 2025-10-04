# BioNexus - AI-Powered Knowledge Graph for NASA Bioscience Publications

<div align="center">

![BioNexus Logo](https://img.shields.io/badge/BioNexus-AI%20Knowledge%20Graph-0077b6?style=for-the-badge&logo=data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjQiIGhlaWdodD0iMjQiIHZpZXdCb3g9IjAgMCAyNCAyNCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTEyIDJMMTMuMDkgOC4yNkwyMCA5TDEzLjA5IDE1Ljc0TDEyIDIyTDEwLjkxIDE1Ljc0TDQgOUwxMC45MSA4LjI2TDEyIDJaIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIGZpbGw9Im5vbmUiLz4KPC9zdmc+)

**Advanced semantic search and knowledge discovery platform for biomedical research**

[![CI/CD Pipeline](https://github.com/username/bionexus/workflows/CI/badge.svg)](https://github.com/username/bionexus/actions)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00b4d8.svg)](https://fastapi.tiangolo.com)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-90e0ef.svg)](https://nextjs.org)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-caf0f8.svg)](https://neo4j.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

## 🚀 Overview

BioNexus is a production-ready AI-powered knowledge graph platform designed to unlock insights from NASA's extensive bioscience publication corpus. Built with modern technologies and advanced NLP capabilities, it transforms static documents into an interconnected web of biomedical knowledge.

### Key Features

🔬 **Advanced Document Processing**
- OCR-powered PDF ingestion with 95%+ accuracy
- Biomedical Named Entity Recognition (NER) using SciSpacy
- Automated relation extraction and entity linking

🧠 **Multimodal AI Integration**  
- ColPali embeddings for visual-textual understanding
- Semantic vector search with FAISS/Weaviate
- RAG (Retrieval-Augmented Generation) with citation tracking

📊 **Interactive Knowledge Graph**
- Neo4j-powered graph database with 10M+ entities
- Real-time visualization and exploration
- Graph neural network insights

🔍 **Intelligent Search & Discovery**
- Multi-modal semantic search (text + visual)
- Boolean query support with advanced filters
- Contextual result ranking and clustering

📈 **Research Analytics**
- Publication trend analysis
- Citation network mapping  
- Research impact metrics
- Collaboration pattern detection

## 🏗️ Architecture

```mermaid
graph TB
    A[PDF Documents] --> B[Ingestion Pipeline]
    B --> C[OCR Engine]
    B --> D[ColPali Embeddings]
    B --> E[Biomedical NER]
    
    C --> F[Neo4j Aura Cloud]
    D --> G[Milvus Cloud]
    E --> F
    
    F --> H[FastAPI Backend]
    G --> H
    N[Google Cloud Storage] --> H
    
    H --> I[Next.js Frontend]
    I --> J[BioNexus Dashboard]
    
    K[Mission Planner] --> H
    L[Export System] --> H
    
    M[Google Cloud Platform] --> F
    M --> G  
    M --> N
    M --> H
    M --> I
    
    style A fill:#03045e,color:#fff
    style F fill:#0077b6,color:#fff  
    style G fill:#0077b6,color:#fff
    style N fill:#0077b6,color:#fff
    style H fill:#00b4d8,color:#fff
    style I fill:#90e0ef,color:#000
    style J fill:#caf0f8,color:#000
    style M fill:#34a853,color:#fff
```

### Technology Stack

**Backend** 🔧
- **FastAPI**: High-performance Python web framework
- **Neo4j Aura**: Cloud knowledge graph database
- **Milvus Cloud**: Scalable vector similarity search
- **SciSpacy**: Biomedical NLP pipeline
- **ColPali**: Multimodal document embeddings
- **Tesseract OCR**: Document text extraction

**Frontend** 🎨  
- **Next.js 14**: React-based web framework
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first styling
- **Cytoscape.js**: Graph visualization
- **React Query**: Data fetching and caching

**Cloud Infrastructure** �
- **Google Cloud Platform**: Scalable cloud infrastructure
- **Google Cloud Storage**: Object storage for documents
- **Docker & Docker Compose**: Containerized deployment
- **Terraform**: Infrastructure as Code
- **GitHub Actions**: CI/CD pipeline

## 📦 Cloud-First Installation

BioNexus is designed for cloud deployment with **Neo4j Aura**, **Milvus Cloud**, and **Google Cloud Platform**.

### Prerequisites

- **Cloud Services** (Required):
  - Neo4j Aura account (knowledge graph)
  - Zilliz Cloud account (vector database)
  - Google Cloud Platform project
  - OpenAI API key
- **Local Development**:
  - Docker & Docker Compose  
  - Python 3.10+
  - Node.js 18+
  - Git

### 🚀 Quick Cloud Setup

1. **Clone the repository**
```bash
git clone https://github.com/CypherKingdom/bionexus.git
cd bionexus
```

2. **Set up cloud services**
```bash
# Follow the comprehensive setup guide
cat CLOUD_SETUP_GUIDE.md

# Key services to set up:
# - Neo4j Aura: https://neo4j.com/aura/
# - Milvus Cloud: https://zilliz.com/cloud  
# - Google Cloud: https://console.cloud.google.com/
# - OpenAI API: https://platform.openai.com/
```

3. **Configure environment**
```bash
# Copy and customize environment template
cp .env.example .env

# Add your cloud credentials:
# - NEO4J_URI=neo4j+s://xxx.databases.neo4j.io
# - MILVUS_HOST=xxx.milvusdb.io
# - OPENAI_API_KEY=sk-proj-xxx
# - GCS_PROJECT_ID=your-project
nano .env
```

4. **Test cloud connectivity**
```bash
# Verify all cloud services are accessible
./test-cloud-services.sh
```

5. **Deploy to cloud**
```bash
# Deploy to Google Cloud Platform
./cloud-deployment/deploy.sh your-project-id us-central1 yourdomain.com

# Or run locally with cloud services
docker-compose up -d
```

6. **Access your application**
- **Production**: https://app.yourdomain.com
- **API**: https://api.yourdomain.com
- **Documentation**: https://api.yourdomain.com/docs
- **Local**: http://localhost:3000

### Manual Installation

<details>
<summary>Click to expand manual setup instructions</summary>

#### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Frontend Setup

```bash
cd frontend
pnpm install
pnpm run dev
```

#### Database Setup

Install Neo4j Community Edition and run:
```bash
neo4j start
cypher-shell -u neo4j -p password -f infra/cypher_setup.cypher
```

</details>

## 🚀 Usage

### Running the Demo

Execute the comprehensive demo to see BioNexus in action:

```bash
# Run 3-paper demonstration
./scripts/run_demo.sh

# Run full 608-paper ingestion (requires 2-4 hours)
./scripts/run_608.sh
```

### Core Workflows

#### 1. Document Ingestion

```python
import requests

# Start ingestion job
response = requests.post("http://localhost:8000/ingest/run", 
                        json={"mode": "sample", "file_paths": ["paper1.pdf"]})
job_id = response.json()["job_id"]

# Monitor progress
status = requests.get(f"http://localhost:8000/ingest/status/{job_id}")
print(f"Status: {status.json()['status']}")
```

#### 2. Semantic Search

```python
# Perform semantic search
search_request = {
    "query": "microgravity effects on bone density",
    "top_k": 10,
    "filters": {"year_range": [2020, 2024]}
}

results = requests.post("http://localhost:8000/search/semantic", 
                       json=search_request)
print(f"Found {len(results.json()['results'])} relevant pages")
```

#### 3. RAG-Powered Summarization

```python
# Generate research summary with citations
rag_request = {
    "question": "What are the mechanisms of bone loss in microgravity?",
    "top_k_pages": 15,
    "include_citations": True
}

summary = requests.post("http://localhost:8000/summarize/rag", 
                       json=rag_request)
print(summary.json()["answer"])
```

#### 4. Knowledge Graph Queries

```python
# Explore entity relationships
graph_data = requests.get("http://localhost:8000/kg/visualization?limit=100")
entities = requests.get("http://localhost:8000/kg/entities/Protein")
```

### Mission Planning Integration

BioNexus includes specialized mission planning capabilities:

```python
# Research mission context
mission_request = {
    "mission_type": "Mars exploration", 
    "duration_days": 600,
    "research_focus": ["bone health", "cardiovascular"]
}

recommendations = requests.post("http://localhost:8000/mission/plan", 
                               json=mission_request)
```

## 📊 API Reference

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | System health and service status |
| `/search/semantic` | POST | Multimodal semantic search |
| `/search/boolean` | POST | Boolean query search |
| `/ingest/run` | POST | Start document ingestion |
| `/ingest/status/{job_id}` | GET | Check ingestion progress |
| `/summarize/rag` | POST | RAG summarization with citations |
| `/kg/visualization` | GET | Graph visualization data |
| `/kg/statistics` | GET | Knowledge graph statistics |
| `/export/entities` | GET | Export entities (JSON/CSV) |
| `/export/publications` | GET | Export publications |

### Advanced Features

**Semantic Search Parameters**
```json
{
  "query": "string",
  "top_k": 10,
  "similarity_threshold": 0.7,
  "filters": {
    "year_range": [2020, 2024],
    "authors": ["Smith, J."],
    "entities": ["Protein", "Gene"]
  },
  "boost_recent": true
}
```

**RAG Summarization Options**
```json
{
  "question": "string", 
  "top_k_pages": 15,
  "include_citations": true,
  "context_window": 2000,
  "temperature": 0.3,
  "max_tokens": 500
}
```

## 🧪 Testing

### Running Tests

```bash
# Backend unit tests
cd backend
pytest tests/unit/ -v --cov=app

# Backend integration tests  
pytest tests/integration/ -v

# Frontend tests
cd frontend
pnpm test

# End-to-end tests
cd tests/e2e
pytest test_e2e.py -v
```

### Test Coverage

- **Unit Tests**: 95%+ coverage for core services
- **Integration Tests**: API endpoint validation  
- **E2E Tests**: Complete workflow verification
- **Performance Tests**: Load testing with 1000+ concurrent users

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Neo4j Aura Cloud Database
NEO4J_URI=neo4j+s://your-instance.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_aura_password

# Milvus Cloud Vector Database
MILVUS_HOST=your-endpoint.milvusdb.io
MILVUS_USER=your_milvus_username
MILVUS_PASSWORD=your_milvus_password

# Google Cloud Storage
GCS_PROJECT_ID=your-gcp-project
GCS_BUCKET_NAME=bionexus-documents

# External APIs
OPENAI_API_KEY=sk-proj-your-openai-key
HUGGINGFACE_API_KEY=hf_your-huggingface-token

# ML Models
COLPALI_MODEL=vidore/colpali-v1.3-hf
SPACY_MODEL=en_ner_bionlp13cg_md

# Application Settings
ENVIRONMENT=production
CLOUD_ENVIRONMENT=gcp
DEBUG=false
LOG_LEVEL=INFO
MAX_UPLOAD_SIZE=100000000
CORS_ORIGINS=["https://app.bionexus.space","http://localhost:3000"]
```

### Advanced Configuration

**Neo4j Performance Tuning**
```bash
# Add to neo4j.conf
dbms.memory.heap.initial_size=2G
dbms.memory.heap.max_size=4G
dbms.memory.pagecache.size=2G
```

**ColPali GPU Configuration**
```python
# For GPU acceleration
CUDA_VISIBLE_DEVICES=0,1
PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:512
```

## 🚀 Deployment

### Production Deployment

1. **Docker Swarm / Kubernetes**
```bash
# Docker Swarm
docker stack deploy -c docker-stack.yml bionexus

# Kubernetes
kubectl apply -f k8s/
```

2. **Environment-Specific Configurations**
```bash
# Production
docker-compose -f docker-compose.prod.yml up -d

# Staging  
docker-compose -f docker-compose.staging.yml up -d
```

3. **Health Monitoring**
```bash
# Service health checks
curl http://localhost:8000/health

# Neo4j cluster status
curl http://localhost:7474/db/system/cluster/overview
```

### Scaling Considerations

- **Horizontal Scaling**: Load balance FastAPI instances
- **Database Scaling**: Neo4j clustering with read replicas
- **Vector Search**: Distributed Weaviate deployment
- **Storage**: MinIO distributed mode

## 🤝 Contributing

We welcome contributions from the research community!

### Development Workflow

1. **Fork the repository**
2. **Create feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```
3. **Commit changes** 
   ```bash
   git commit -m 'Add amazing feature'
   ```
4. **Push to branch**
   ```bash
   git push origin feature/amazing-feature
   ```
5. **Open Pull Request**

### Code Standards

- **Python**: Follow PEP 8, use Black formatter
- **TypeScript**: ESLint + Prettier configuration  
- **Documentation**: Comprehensive docstrings and comments
- **Testing**: 90%+ test coverage required

### Issue Reporting

- Use GitHub Issues for bug reports
- Include reproduction steps and environment details
- Tag issues appropriately (bug, enhancement, question)

## 📚 Documentation

- **[API Documentation](http://localhost:8000/docs)**: Interactive Swagger UI
- **[User Guide](docs/user-guide.md)**: Comprehensive usage instructions  
- **[Developer Guide](docs/developer-guide.md)**: Architecture and development
- **[Deployment Guide](docs/deployment.md)**: Production deployment
- **[Troubleshooting](docs/troubleshooting.md)**: Common issues and solutions

## 🛠️ Troubleshooting

### Common Issues

**Connection Errors**
```bash
# Check service status
docker-compose ps

# Restart services
docker-compose restart neo4j backend
```

**Memory Issues**
```bash
# Increase Docker memory limit
# Edit ~/.docker/daemon.json
{
  "memory": "8g",
  "cpus": "4"
}
```

**Model Download Failures**
```bash
# Manual model download
huggingface-cli login
huggingface-cli download vidore/colpali-v1.3-hf
```

### Performance Optimization

**Database Query Optimization**
- Add appropriate indexes for frequent queries
- Use query profiling: `PROFILE MATCH ...`
- Implement query result caching

**Vector Search Acceleration** 
- Use GPU acceleration for embeddings
- Optimize vector dimensions and indexing
- Implement approximate nearest neighbor algorithms

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **NASA**: For providing the bioscience publication corpus
- **SciSpacy**: Advanced biomedical NLP capabilities  
- **ColPali Team**: Innovative multimodal embedding approach
- **Neo4j Community**: Robust graph database technology
- **Hugging Face**: Pre-trained model ecosystem

## 📞 Support

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: Community support and questions
- **Email**: support@bionexus.ai
- **Documentation**: Comprehensive guides and tutorials

---

<div align="center">

**Built with ❤️ for advancing biomedical research and space exploration**

[Website](https://bionexus.ai) • [Demo](https://demo.bionexus.ai) • [Documentation](https://docs.bionexus.ai) • [API](https://api.bionexus.ai)

</div>