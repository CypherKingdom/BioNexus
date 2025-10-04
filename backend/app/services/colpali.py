import torch
from transformers import AutoProcessor, AutoModel
from PIL import Image
import numpy as np
from typing import List, Union
import logging
import os
from sentence_transformers import SentenceTransformer
import faiss

logger = logging.getLogger(__name__)


class ColPaliService:
    def __init__(self, fallback_to_cpu: bool = True):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.fallback_to_cpu = fallback_to_cpu
        self.model = None
        self.processor = None
        self.fallback_model = None
        self.embedding_dim = None
        
        # Initialize models
        self._initialize_models()
    
    def _initialize_models(self):
        """Initialize ColPali model or fallback to sentence transformer."""
        try:
            # Try to load ColPali model
            model_name = "vidore/colpali-v1.3-hf"
            self.processor = AutoProcessor.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name).to(self.device)
            self.embedding_dim = self.model.config.hidden_size
            logger.info(f"Loaded ColPali model on {self.device}")
            
        except Exception as e:
            logger.warning(f"Failed to load ColPali model: {e}")
            
            if self.fallback_to_cpu:
                logger.info("Falling back to sentence transformer for CPU processing")
                self.fallback_model = SentenceTransformer('all-MiniLM-L6-v2')
                self.embedding_dim = 384  # MiniLM embedding dimension
            else:
                raise Exception("ColPali model unavailable and CPU fallback disabled")
    
    def encode_image_and_text(self, image: Image.Image, text: str) -> np.ndarray:
        """Generate multimodal embeddings for image and text."""
        if self.model is not None:
            return self._encode_with_colpali(image, text)
        elif self.fallback_model is not None:
            return self._encode_with_fallback(text)
        else:
            raise Exception("No embedding model available")
    
    def _encode_with_colpali(self, image: Image.Image, text: str) -> np.ndarray:
        """Encode using ColPali multimodal model."""
        try:
            # Prepare inputs
            inputs = self.processor(
                images=image,
                text=text,
                return_tensors="pt",
                padding=True,
                truncation=True
            ).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self.model(**inputs)
                embeddings = outputs.last_hidden_state.mean(dim=1)  # Pool over sequence
                
            # Convert to numpy and normalize
            embeddings_np = embeddings.cpu().numpy().astype(np.float32)
            embeddings_np = embeddings_np / np.linalg.norm(embeddings_np, axis=1, keepdims=True)
            
            return embeddings_np[0]  # Return first (and only) embedding
            
        except Exception as e:
            logger.error(f"ColPali encoding failed: {e}")
            # Fallback to text-only if image processing fails
            return self._encode_with_fallback(text)
    
    def _encode_with_fallback(self, text: str) -> np.ndarray:
        """Encode using fallback sentence transformer (text-only)."""
        try:
            embedding = self.fallback_model.encode(text, normalize_embeddings=True)
            return embedding.astype(np.float32)
        except Exception as e:
            logger.error(f"Fallback encoding failed: {e}")
            # Return zero embedding as last resort
            return np.zeros(self.embedding_dim, dtype=np.float32)
    
    def encode_query(self, query: str) -> np.ndarray:
        """Encode text query for semantic search."""
        if self.model is not None:
            # For ColPali, we can encode text-only queries
            try:
                inputs = self.processor(
                    text=query,
                    return_tensors="pt",
                    padding=True,
                    truncation=True
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    embeddings = outputs.last_hidden_state.mean(dim=1)
                
                embeddings_np = embeddings.cpu().numpy().astype(np.float32)
                embeddings_np = embeddings_np / np.linalg.norm(embeddings_np, axis=1, keepdims=True)
                return embeddings_np[0]
                
            except Exception as e:
                logger.warning(f"ColPali query encoding failed, using fallback: {e}")
                
        # Use fallback model
        return self._encode_with_fallback(query)
    
    def batch_encode_pages(self, pages_data: List[dict], batch_size: int = 8) -> List[np.ndarray]:
        """Batch encode multiple pages for efficiency."""
        embeddings = []
        
        for i in range(0, len(pages_data), batch_size):
            batch = pages_data[i:i + batch_size]
            batch_embeddings = []
            
            for page_data in batch:
                try:
                    if 'image_path' in page_data and os.path.exists(page_data['image_path']):
                        image = Image.open(page_data['image_path']).convert('RGB')
                        embedding = self.encode_image_and_text(image, page_data['text'])
                    else:
                        embedding = self.encode_query(page_data['text'])
                    
                    batch_embeddings.append(embedding)
                    
                except Exception as e:
                    logger.error(f"Failed to encode page: {e}")
                    # Add zero embedding for failed pages
                    batch_embeddings.append(np.zeros(self.embedding_dim, dtype=np.float32))
            
            embeddings.extend(batch_embeddings)
            logger.info(f"Encoded batch {i//batch_size + 1}/{(len(pages_data)-1)//batch_size + 1}")
        
        return embeddings


class VectorSearchService:
    def __init__(self, embedding_dim: int = 384):
        self.embedding_dim = embedding_dim
        self.index = None
        self.page_metadata = []
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize FAISS index for vector search."""
        try:
            # Use inner product for cosine similarity with normalized vectors
            self.index = faiss.IndexFlatIP(self.embedding_dim)
            logger.info(f"Initialized FAISS index with dimension {self.embedding_dim}")
        except Exception as e:
            logger.error(f"Failed to initialize FAISS index: {e}")
            raise
    
    def add_embeddings(self, embeddings: List[np.ndarray], metadata: List[dict]):
        """Add embeddings to the search index."""
        if not embeddings:
            return
        
        try:
            # Stack embeddings into array
            embeddings_array = np.stack(embeddings).astype(np.float32)
            
            # Add to index
            self.index.add(embeddings_array)
            
            # Store metadata
            self.page_metadata.extend(metadata)
            
            logger.info(f"Added {len(embeddings)} embeddings to index. Total: {self.index.ntotal}")
            
        except Exception as e:
            logger.error(f"Failed to add embeddings to index: {e}")
            raise
    
    def search(self, query_embedding: np.ndarray, top_k: int = 10) -> List[dict]:
        """Search for similar pages using vector similarity."""
        if self.index.ntotal == 0:
            return []
        
        try:
            # Reshape query embedding for FAISS
            query_array = query_embedding.reshape(1, -1).astype(np.float32)
            
            # Search
            scores, indices = self.index.search(query_array, min(top_k, self.index.ntotal))
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if idx != -1 and idx < len(self.page_metadata):  # Valid result
                    metadata = self.page_metadata[idx].copy()
                    metadata['score'] = float(score)
                    metadata['rank'] = i + 1
                    results.append(metadata)
            
            return results
            
        except Exception as e:
            logger.error(f"Vector search failed: {e}")
            return []
    
    def save_index(self, filepath: str):
        """Save the FAISS index to disk."""
        try:
            faiss.write_index(self.index, filepath)
            logger.info(f"Saved FAISS index to {filepath}")
        except Exception as e:
            logger.error(f"Failed to save index: {e}")
    
    def load_index(self, filepath: str):
        """Load the FAISS index from disk."""
        try:
            self.index = faiss.read_index(filepath)
            logger.info(f"Loaded FAISS index from {filepath}")
        except Exception as e:
            logger.error(f"Failed to load index: {e}")


# Global service instances
colpali_service = ColPaliService()
vector_search_service = VectorSearchService(embedding_dim=colpali_service.embedding_dim)