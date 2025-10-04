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
    
    # Database
    neo4j_uri: str = "bolt://localhost:7687"
    neo4j_user: str = "neo4j"
    neo4j_password: str = "password"
    neo4j_database: str = "neo4j"
    
    # Vector Database
    weaviate_url: str = "http://localhost:8080"
    weaviate_api_key: str = ""
    faiss_index_path: str = "./data/faiss_index"
    
    # Object Storage
    minio_endpoint: str = "localhost:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket_name: str = "bionexus"
    minio_secure: bool = False
    
    # ML Models
    huggingface_api_key: str = ""
    colpali_model: str = "vidore/colpali-v1.3-hf"
    spacy_model: str = "en_ner_bionlp13cg_md"
    device: str = "auto"
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
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
    
    # Cache
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    class Config:
        env_file = ".env"
        case_sensitive = False

# Global settings instance
settings = Settings()