"""
Google Cloud Storage Client for BioNexus
Handles document storage, retrieval, and management in Google Cloud Storage.
"""

import logging
from typing import BinaryIO, List, Dict, Any, Optional
import os
from datetime import datetime, timedelta
import json

try:
    from google.cloud import storage
    from google.oauth2 import service_account
    GCS_AVAILABLE = True
except ImportError:
    GCS_AVAILABLE = False

from ..config import settings

logger = logging.getLogger(__name__)


class GoogleCloudStorageClient:
    """Google Cloud Storage client for document management."""
    
    def __init__(self):
        self.bucket_name = settings.gcs_bucket_name
        self.project_id = settings.gcs_project_id
        self.credentials_path = settings.gcs_credentials_path
        self.client = None
        self.bucket = None
        
        if GCS_AVAILABLE and self.bucket_name:
            self._initialize_client()
        else:
            logger.warning("Google Cloud Storage not available - using mock client")

    def _initialize_client(self):
        """Initialize the Google Cloud Storage client."""
        try:
            # Initialize with service account credentials if provided
            if self.credentials_path and os.path.exists(self.credentials_path):
                credentials = service_account.Credentials.from_service_account_file(
                    self.credentials_path
                )
                self.client = storage.Client(
                    project=self.project_id,
                    credentials=credentials
                )
            else:
                # Use default credentials (for Cloud Run environment)
                self.client = storage.Client(project=self.project_id)
            
            # Get or create bucket
            try:
                self.bucket = self.client.bucket(self.bucket_name)
                # Test bucket access
                self.bucket.reload()
                logger.info(f"Connected to GCS bucket: {self.bucket_name}")
            except Exception as e:
                logger.error(f"Failed to access bucket {self.bucket_name}: {e}")
                # Try to create bucket if it doesn't exist
                self._create_bucket()
                
        except Exception as e:
            logger.error(f"Failed to initialize GCS client: {e}")

    def _create_bucket(self):
        """Create the storage bucket if it doesn't exist."""
        try:
            self.bucket = self.client.create_bucket(
                self.bucket_name,
                location="US"  # Or use settings.region
            )
            logger.info(f"Created GCS bucket: {self.bucket_name}")
        except Exception as e:
            logger.error(f"Failed to create bucket: {e}")

    def upload_document(
        self, 
        file_content: bytes, 
        filename: str, 
        content_type: str = "application/pdf",
        metadata: Dict[str, Any] = None
    ) -> Optional[str]:
        """Upload a document to Google Cloud Storage."""
        if not self.bucket:
            logger.warning("GCS not available - cannot upload document")
            return None

        try:
            # Create blob with organized path structure
            blob_name = f"documents/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
            blob = self.bucket.blob(blob_name)
            
            # Set metadata
            if metadata:
                blob.metadata = metadata
            
            # Upload file
            blob.upload_from_string(
                file_content,
                content_type=content_type
            )
            
            logger.info(f"Uploaded document to GCS: {blob_name}")
            return blob_name
            
        except Exception as e:
            logger.error(f"Failed to upload document: {e}")
            return None

    def upload_processed_image(
        self, 
        image_data: bytes, 
        document_id: str, 
        page_number: int,
        image_format: str = "png"
    ) -> Optional[str]:
        """Upload a processed page image."""
        if not self.bucket:
            return None

        try:
            blob_name = f"images/{document_id}/page_{page_number:04d}.{image_format}"
            blob = self.bucket.blob(blob_name)
            
            blob.upload_from_string(
                image_data,
                content_type=f"image/{image_format}"
            )
            
            # Generate public URL for frontend access
            public_url = f"https://storage.googleapis.com/{self.bucket_name}/{blob_name}"
            
            logger.info(f"Uploaded page image: {blob_name}")
            return public_url
            
        except Exception as e:
            logger.error(f"Failed to upload image: {e}")
            return None

    def download_document(self, blob_name: str) -> Optional[bytes]:
        """Download a document from Google Cloud Storage."""
        if not self.bucket:
            return None

        try:
            blob = self.bucket.blob(blob_name)
            content = blob.download_as_bytes()
            
            logger.info(f"Downloaded document: {blob_name}")
            return content
            
        except Exception as e:
            logger.error(f"Failed to download document: {e}")
            return None

    def get_signed_url(
        self, 
        blob_name: str, 
        expiration_hours: int = 1,
        method: str = "GET"
    ) -> Optional[str]:
        """Generate a signed URL for secure access to a document."""
        if not self.bucket:
            return None

        try:
            blob = self.bucket.blob(blob_name)
            
            # Generate signed URL
            url = blob.generate_signed_url(
                version="v4",
                expiration=datetime.utcnow() + timedelta(hours=expiration_hours),
                method=method
            )
            
            return url
            
        except Exception as e:
            logger.error(f"Failed to generate signed URL: {e}")
            return None

    def list_documents(
        self, 
        prefix: str = "documents/",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List documents in the storage bucket."""
        if not self.bucket:
            return []

        try:
            blobs = self.client.list_blobs(
                self.bucket_name,
                prefix=prefix,
                max_results=limit
            )
            
            documents = []
            for blob in blobs:
                documents.append({
                    "name": blob.name,
                    "size": blob.size,
                    "created": blob.time_created.isoformat(),
                    "updated": blob.updated.isoformat(),
                    "content_type": blob.content_type,
                    "metadata": blob.metadata or {}
                })
            
            return documents
            
        except Exception as e:
            logger.error(f"Failed to list documents: {e}")
            return []

    def delete_document(self, blob_name: str) -> bool:
        """Delete a document from storage."""
        if not self.bucket:
            return False

        try:
            blob = self.bucket.blob(blob_name)
            blob.delete()
            
            logger.info(f"Deleted document: {blob_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete document: {e}")
            return False

    def delete_document_folder(self, document_id: str) -> bool:
        """Delete all files related to a document."""
        if not self.bucket:
            return False

        try:
            # Delete document file
            document_blobs = self.client.list_blobs(
                self.bucket_name,
                prefix=f"documents/"
            )
            
            # Delete associated images
            image_blobs = self.client.list_blobs(
                self.bucket_name,
                prefix=f"images/{document_id}/"
            )
            
            # Delete all related blobs
            deleted_count = 0
            for blob in list(document_blobs) + list(image_blobs):
                if document_id in blob.name:
                    blob.delete()
                    deleted_count += 1
            
            logger.info(f"Deleted {deleted_count} files for document: {document_id}")
            return deleted_count > 0
            
        except Exception as e:
            logger.error(f"Failed to delete document folder: {e}")
            return False

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get storage usage statistics."""
        if not self.bucket:
            return {}

        try:
            # Count documents and images
            total_size = 0
            document_count = 0
            image_count = 0
            
            for blob in self.client.list_blobs(self.bucket_name):
                total_size += blob.size or 0
                if blob.name.startswith("documents/"):
                    document_count += 1
                elif blob.name.startswith("images/"):
                    image_count += 1
            
            return {
                "bucket_name": self.bucket_name,
                "total_size_bytes": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "document_count": document_count,
                "image_count": image_count,
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get storage stats: {e}")
            return {}


class MockGCSClient:
    """Mock Google Cloud Storage client for when GCS is not available."""
    
    def __init__(self):
        self.storage = {}  # In-memory storage for mock
        logger.info("Using Mock GCS client")

    def upload_document(self, file_content, filename, content_type="application/pdf", metadata=None):
        blob_name = f"documents/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
        self.storage[blob_name] = {
            "content": file_content,
            "content_type": content_type,
            "metadata": metadata or {},
            "created": datetime.now().isoformat()
        }
        return blob_name

    def upload_processed_image(self, image_data, document_id, page_number, image_format="png"):
        blob_name = f"images/{document_id}/page_{page_number:04d}.{image_format}"
        self.storage[blob_name] = {
            "content": image_data,
            "content_type": f"image/{image_format}",
            "created": datetime.now().isoformat()
        }
        return f"mock://storage/{blob_name}"

    def download_document(self, blob_name):
        return self.storage.get(blob_name, {}).get("content")

    def get_signed_url(self, blob_name, expiration_hours=1, method="GET"):
        return f"mock://signed-url/{blob_name}?expires={expiration_hours}h"

    def list_documents(self, prefix="documents/", limit=100):
        documents = []
        for name, data in self.storage.items():
            if name.startswith(prefix):
                documents.append({
                    "name": name,
                    "size": len(data["content"]) if isinstance(data["content"], bytes) else 0,
                    "created": data["created"],
                    "updated": data["created"],
                    "content_type": data["content_type"],
                    "metadata": data["metadata"]
                })
        return documents[:limit]

    def delete_document(self, blob_name):
        if blob_name in self.storage:
            del self.storage[blob_name]
            return True
        return False

    def delete_document_folder(self, document_id):
        to_delete = [name for name in self.storage.keys() if document_id in name]
        for name in to_delete:
            del self.storage[name]
        return len(to_delete) > 0

    def get_storage_stats(self):
        total_size = sum(
            len(data["content"]) if isinstance(data["content"], bytes) else 0 
            for data in self.storage.values()
        )
        return {
            "bucket_name": "mock_bucket",
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024 * 1024), 2),
            "document_count": len([k for k in self.storage.keys() if k.startswith("documents/")]),
            "image_count": len([k for k in self.storage.keys() if k.startswith("images/")]),
            "last_updated": datetime.now().isoformat()
        }


# Initialize the appropriate client
if GCS_AVAILABLE and settings.gcs_bucket_name:
    storage_client = GoogleCloudStorageClient()
else:
    storage_client = MockGCSClient()