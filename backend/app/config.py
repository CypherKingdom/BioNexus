# BioNexus Backend Configuration
import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application
    app_name: str = "BioNexus"
    debug: bool = False
    version: str = "1.0.0"
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 4
    
    # Neo4j Aura (Cloud Knowledge Graph)
    neo4j_uri: str = os.getenv("NEO4J_URI", "neo4j+s://your-neo4j-instance.databases.neo4j.io")
    neo4j_user: str = os.getenv("NEO4J_USERNAME", "neo4j")
    neo4j_password: str = os.getenv("NEO4J_PASSWORD", "")
    neo4j_database: str = "neo4j"
    
    # Milvus Cloud (Vector Database)
    milvus_uri: str = os.getenv("MILVUS_URI", "")
    milvus_token: str = os.getenv("MILVUS_TOKEN", "")
    milvus_collection_name: str = "bionexus_embeddings"
    
    # Google Cloud Storage (Object Storage)
    gcs_bucket_name: str = "bionexus-documents"
    gcs_credentials_path: str = ""  # Path to service account JSON
    gcs_project_id: str = ""
    

    
    # ML Models
    huggingface_api_key: str = ""
    colpali_model: str = "vidore/colpali-v1.3-hf"
    spacy_model: str = "en_ner_bionlp13cg_md"
    device: str = "auto"
    
    # CORS (Updated for Cloud Deployment)
    cors_origins: List[str] = [
        "http://localhost:3000", 
        "http://localhost:3001",
        "https://app.bionexus.space",
        "https://bionexus.space",
        "https://*.run.app",  # Google Cloud Run domains
        "https://*.googleusercontent.com"  # Google Cloud domains
    ]
    
    # File Processing
    max_upload_size: int = 100_000_000  # 100MB
    batch_size: int = 32
    max_pages_per_pdf: int = 500
    ocr_timeout: int = 300
    embedding_timeout: int = 600
    
    # Logging
    log_level: str = "INFO"
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30
    
    # Google Cloud Memorystore (Redis)
    redis_url: str = "redis://10.0.0.1:6379"  # Internal GCP Redis instance
    cache_ttl: int = 3600
    
    # Cloud Environment
    cloud_environment: str = "gcp"  # gcp, aws, azure
    environment: str = "production"  # development, staging, production
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields in .env

# Global settings instance
settings = Settings()