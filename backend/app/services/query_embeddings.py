"""
Simplified query embedding service for read-only BioNexus backend.
Only handles query embeddings for semantic search against pre-computed embeddings.
"""

import logging
import numpy as np
from typing import Optional

# Optional imports for embeddings
try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None

logger = logging.getLogger(__name__)


class QueryEmbeddingService:
    """Lightweight service for query embeddings only - no document processing."""
    
    def __init__(self):
        self.enabled = False
        self.model = None
        self.embedding_dim = 384  # Default embedding dimension
        
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self._initialize_model()

    def _initialize_model(self):
        """Initialize sentence transformer for query encoding."""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            self.embedding_dim = 384  # MiniLM embedding dimension
            self.enabled = True
            logger.info("Initialized query embedding model (Sentence Transformer)")
            
        except Exception as e:
            logger.warning(f"Failed to load query embedding model: {e}")
            logger.warning("Query embeddings will be disabled")

    def encode_query(self, query: str) -> np.ndarray:
        """Encode text query for semantic search against pre-computed embeddings."""
        if not self.enabled or not self.model:
            logger.warning("Query embedding service is disabled - returning zero embedding")
            return np.zeros(self.embedding_dim, dtype=np.float32)
        
        try:
            embedding = self.model.encode(query, normalize_embeddings=True)
            return embedding.astype(np.float32)
            
        except Exception as e:
            logger.error(f"Query encoding failed: {e}")
            return np.zeros(self.embedding_dim, dtype=np.float32)

    def batch_encode_queries(self, queries: list) -> list:
        """Batch encode multiple queries for efficiency."""
        if not self.enabled or not self.model:
            logger.warning("Query embedding service is disabled")
            return [np.zeros(self.embedding_dim, dtype=np.float32) for _ in queries]
        
        try:
            embeddings = self.model.encode(queries, normalize_embeddings=True, batch_size=8)
            return [emb.astype(np.float32) for emb in embeddings]
            
        except Exception as e:
            logger.error(f"Batch query encoding failed: {e}")
            return [np.zeros(self.embedding_dim, dtype=np.float32) for _ in queries]


# Create global service instance
query_embedding_service = QueryEmbeddingService()