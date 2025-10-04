"""
Milvus Cloud Vector Database Client for BioNexus
Provides vector storage and similarity search capabilities using Milvus Cloud.
"""

import logging
from typing import List, Dict, Any, Optional
import numpy as np
from datetime import datetime

try:
    from pymilvus import (
        connections, Collection, CollectionSchema, FieldSchema, DataType,
        utility, db
    )
    MILVUS_AVAILABLE = True
except ImportError:
    MILVUS_AVAILABLE = False

from ..config import settings

logger = logging.getLogger(__name__)


class MilvusClient:
    """Milvus Cloud client for vector operations."""
    
    def __init__(self):
        self.host = settings.milvus_host
        self.port = settings.milvus_port
        self.user = settings.milvus_user
        self.password = settings.milvus_password
        self.collection_name = settings.milvus_collection_name
        self.collection = None
        self.connected = False
        
        if MILVUS_AVAILABLE and self.host:
            self.connect()
        else:
            logger.warning("Milvus not available or not configured - using mock client")

    def connect(self):
        """Connect to Milvus Cloud."""
        try:
            connections.connect(
                alias="default",
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                secure=settings.milvus_secure
            )
            
            # Create collection if it doesn't exist
            self._create_collection_if_not_exists()
            self.connected = True
            logger.info(f"Connected to Milvus Cloud at {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to connect to Milvus: {e}")
            self.connected = False

    def _create_collection_if_not_exists(self):
        """Create the BioNexus collection if it doesn't exist."""
        if utility.has_collection(self.collection_name):
            self.collection = Collection(self.collection_name)
            logger.info(f"Using existing collection: {self.collection_name}")
            return

        # Define collection schema
        fields = [
            FieldSchema(
                name="id", 
                dtype=DataType.VARCHAR, 
                is_primary=True, 
                max_length=100
            ),
            FieldSchema(
                name="document_id", 
                dtype=DataType.VARCHAR, 
                max_length=100
            ),
            FieldSchema(
                name="page_id", 
                dtype=DataType.VARCHAR, 
                max_length=100
            ),
            FieldSchema(
                name="embedding", 
                dtype=DataType.FLOAT_VECTOR, 
                dim=1024  # ColPali embedding dimension
            ),
            FieldSchema(
                name="text_content", 
                dtype=DataType.VARCHAR, 
                max_length=65535
            ),
            FieldSchema(
                name="metadata", 
                dtype=DataType.JSON
            ),
            FieldSchema(
                name="created_at", 
                dtype=DataType.VARCHAR, 
                max_length=50
            )
        ]
        
        schema = CollectionSchema(
            fields=fields, 
            description="BioNexus document embeddings collection"
        )
        
        # Create collection
        self.collection = Collection(
            name=self.collection_name,
            schema=schema
        )
        
        # Create index for vector field
        index_params = {
            "metric_type": "COSINE",
            "index_type": "HNSW",
            "params": {"M": 8, "efConstruction": 64}
        }
        
        self.collection.create_index(
            field_name="embedding",
            index_params=index_params
        )
        
        logger.info(f"Created collection: {self.collection_name}")

    def insert_embeddings(
        self, 
        embeddings: List[List[float]], 
        document_ids: List[str],
        page_ids: List[str],
        text_contents: List[str],
        metadata_list: List[Dict[str, Any]]
    ) -> List[str]:
        """Insert document embeddings into Milvus."""
        if not self.connected:
            logger.warning("Milvus not connected - skipping insertion")
            return []

        try:
            # Generate unique IDs
            ids = [f"{doc_id}_{page_id}_{i}" for i, (doc_id, page_id) in enumerate(zip(document_ids, page_ids))]
            
            # Prepare data
            data = [
                ids,
                document_ids,
                page_ids,
                embeddings,
                text_contents,
                metadata_list,
                [datetime.now().isoformat()] * len(ids)
            ]
            
            # Insert data
            insert_result = self.collection.insert(data)
            
            # Ensure data is persisted
            self.collection.flush()
            
            logger.info(f"Inserted {len(ids)} embeddings into Milvus")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to insert embeddings: {e}")
            return []

    def search_similar(
        self, 
        query_embedding: List[float], 
        top_k: int = 10,
        similarity_threshold: float = 0.7
    ) -> List[Dict[str, Any]]:
        """Search for similar embeddings."""
        if not self.connected:
            logger.warning("Milvus not connected - returning empty results")
            return []

        try:
            # Load collection for search
            self.collection.load()
            
            # Search parameters
            search_params = {
                "metric_type": "COSINE",
                "params": {"ef": 64}
            }
            
            # Perform search
            results = self.collection.search(
                data=[query_embedding],
                anns_field="embedding",
                param=search_params,
                limit=top_k,
                expr=None,
                output_fields=["document_id", "page_id", "text_content", "metadata", "created_at"]
            )
            
            # Process results
            search_results = []
            for hits in results:
                for hit in hits:
                    if hit.score >= similarity_threshold:
                        search_results.append({
                            "id": hit.id,
                            "document_id": hit.entity.get("document_id"),
                            "page_id": hit.entity.get("page_id"),
                            "text_content": hit.entity.get("text_content"),
                            "metadata": hit.entity.get("metadata", {}),
                            "similarity_score": float(hit.score),
                            "created_at": hit.entity.get("created_at")
                        })
            
            logger.info(f"Found {len(search_results)} similar results")
            return search_results
            
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def delete_by_document_id(self, document_id: str) -> bool:
        """Delete all embeddings for a specific document."""
        if not self.connected:
            return False

        try:
            # Delete by expression
            expr = f'document_id == "{document_id}"'
            self.collection.delete(expr)
            self.collection.flush()
            
            logger.info(f"Deleted embeddings for document: {document_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete embeddings: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get collection statistics."""
        if not self.connected:
            return {}

        try:
            stats = self.collection.get_stats()
            return {
                "total_entities": stats.row_count,
                "collection_name": self.collection_name,
                "schema": self.collection.schema.to_dict()
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {}

    def create_collection_backup(self, backup_name: str) -> bool:
        """Create a backup of the collection."""
        if not self.connected:
            return False

        try:
            # Implementation depends on Milvus backup capabilities
            logger.info(f"Collection backup functionality not implemented: {backup_name}")
            return False
        except Exception as e:
            logger.error(f"Backup failed: {e}")
            return False

    def disconnect(self):
        """Disconnect from Milvus."""
        try:
            if self.connected:
                connections.disconnect("default")
                self.connected = False
                logger.info("Disconnected from Milvus")
        except Exception as e:
            logger.error(f"Error disconnecting from Milvus: {e}")


class MockMilvusClient:
    """Mock Milvus client for when Milvus is not available."""
    
    def __init__(self):
        self.embeddings_store = []
        logger.info("Using Mock Milvus client")

    def connect(self):
        pass

    def insert_embeddings(self, embeddings, document_ids, page_ids, text_contents, metadata_list):
        # Store in memory for mock
        for i, embedding in enumerate(embeddings):
            self.embeddings_store.append({
                "id": f"mock_{i}",
                "document_id": document_ids[i] if i < len(document_ids) else f"doc_{i}",
                "page_id": page_ids[i] if i < len(page_ids) else f"page_{i}",
                "embedding": embedding,
                "text_content": text_contents[i] if i < len(text_contents) else "",
                "metadata": metadata_list[i] if i < len(metadata_list) else {},
                "created_at": datetime.now().isoformat()
            })
        return [f"mock_{i}" for i in range(len(embeddings))]

    def search_similar(self, query_embedding, top_k=10, similarity_threshold=0.7):
        # Simple cosine similarity for mock
        results = []
        for item in self.embeddings_store:
            # Mock similarity calculation
            similarity = 0.8  # Mock high similarity
            if similarity >= similarity_threshold:
                results.append({
                    "id": item["id"],
                    "document_id": item["document_id"],
                    "page_id": item["page_id"],
                    "text_content": item["text_content"],
                    "metadata": item["metadata"],
                    "similarity_score": similarity,
                    "created_at": item["created_at"]
                })
        
        return results[:top_k]

    def delete_by_document_id(self, document_id):
        initial_count = len(self.embeddings_store)
        self.embeddings_store = [
            item for item in self.embeddings_store 
            if item["document_id"] != document_id
        ]
        return len(self.embeddings_store) < initial_count

    def get_collection_stats(self):
        return {
            "total_entities": len(self.embeddings_store),
            "collection_name": "mock_collection",
            "schema": "mock_schema"
        }

    def disconnect(self):
        pass


# Initialize the appropriate client
if MILVUS_AVAILABLE and settings.milvus_host:
    milvus_client = MilvusClient()
else:
    milvus_client = MockMilvusClient()