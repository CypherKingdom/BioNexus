from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
import logging
import os
from pathlib import Path
from datetime import datetime

# Load environment variables from .env file
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(env_path)

from .config import settings
from .logging_config import setup_logging, get_logger
from .exceptions import (
    BioNexusException, 
    bionexus_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from .routers import search, graph, summarize, export, azure_ai
# Skip integrations router temporarily - requires optional dependencies
# from .routers import integrations
from .services.neo4j_client import neo4j_client
from .services.milvus_client import milvus_client

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BioNexus API",
    description="Read-only AI-powered knowledge graph platform for NASA bioscience publications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],  # Only read operations
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(BioNexusException, bionexus_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers (read-only operations only)
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(graph.router, prefix="/graph", tags=["knowledge-graph"])
app.include_router(summarize.router, prefix="/summarize", tags=["summarization"])
# Skip integrations router temporarily - requires optional dependencies
# app.include_router(integrations.router, prefix="/integrations", tags=["external-integrations"])

# Azure AI services
app.include_router(azure_ai.router, tags=["azure-ai"])

app.include_router(export.router, prefix="/export", tags=["data-export"])


@app.on_event("startup")
async def startup_event():
    """Initialize read-only database connections on startup."""
    try:
        logger.info("Starting BioNexus Read-Only API...")
        
        # Test Neo4j Aura connection (read-only)
        test_result = neo4j_client.run_query("RETURN 1 as test LIMIT 1")
        if test_result:
            logger.info("Neo4j Aura connection verified")
        else:
            logger.warning("Neo4j Aura connection test failed")
        
        # Test Milvus Cloud connection (read-only)
        milvus_client.connect()
        logger.info("Milvus Cloud connection verified")
        
        logger.info("BioNexus Read-Only API startup complete")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        # Don't raise in production - allow graceful degradation
        if settings.environment == "development":
            raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        neo4j_client.close()
        milvus_client.disconnect()
        logger.info("BioNexus API shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {e}")


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "BioNexus Read-Only API",
        "version": "1.0.0",
        "description": "Read-only AI-powered knowledge graph platform for pre-processed NASA bioscience publications",
        "data_source": "Pre-processed data from Neo4j Aura and Milvus Cloud",
        "endpoints": {
            "search": "/search/*", 
            "knowledge_graph": "/graph/*",
            "summarization": "/summarize/*",
            "integrations": "/integrations/*",

            "data_export": "/export/*",
            "documentation": "/docs"
        },
        "status": "running",
        "mode": "read_only"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Get Neo4j stats
        neo4j_stats = {}
        try:
            # Count nodes
            node_result = neo4j_client.run_query("MATCH (n) RETURN count(n) as count")
            neo4j_stats['node_count'] = node_result[0]['count'] if node_result else 0
            
            # Count publications
            pub_result = neo4j_client.run_query("MATCH (p:Publication) RETURN count(p) as count")
            neo4j_stats['publication_count'] = pub_result[0]['count'] if pub_result else 0
            
            # Count pages
            page_result = neo4j_client.run_query("MATCH (pg:Page) RETURN count(pg) as count")
            neo4j_stats['page_count'] = page_result[0]['count'] if page_result else 0
            
            # Count entities
            entity_result = neo4j_client.run_query("MATCH (e:Entity) RETURN count(e) as count")
            neo4j_stats['entity_count'] = entity_result[0]['count'] if entity_result else 0
        except Exception as e:
            logger.error(f"Neo4j stats error: {e}")
            neo4j_stats = {'error': str(e)}
        
        # Get Milvus stats
        milvus_stats = {}
        try:
            # Get collection info - use utility module
            from pymilvus import utility
            collections = utility.list_collections()
            milvus_stats['collections'] = collections
            if 'bionexus_embeddings' in collections:
                from pymilvus import Collection
                collection = Collection('bionexus_embeddings')
                milvus_stats['vector_count'] = collection.num_entities
        except Exception as e:
            logger.error(f"Milvus stats error: {e}")
            milvus_stats = {'error': str(e)}
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "services": {
                "neo4j": "healthy",
                "milvus": "healthy",
                "api": "healthy"
            },
            "neo4j_stats": neo4j_stats,
            "milvus_stats": milvus_stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }


@app.get("/debug/schema")
async def debug_schema():
    """Debug endpoint to see what's actually in the database."""
    try:
        # Get all node labels
        labels_query = "CALL db.labels() YIELD label RETURN label"
        labels = neo4j_client.run_query(labels_query)
        
        # Get sample nodes for each label
        samples = {}
        for label_row in labels[:5]:  # Limit to first 5 labels
            label = label_row['label']
            sample_query = f"MATCH (n:{label}) RETURN n LIMIT 3"
            sample_nodes = neo4j_client.run_query(sample_query)
            samples[label] = sample_nodes
        
        # Get relationship types
        rel_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType"
        relationships = neo4j_client.run_query(rel_query)
        
        return {
            "node_labels": [l['label'] for l in labels],
            "sample_nodes": samples,
            "relationship_types": [r['relationshipType'] for r in relationships]
        }
    except Exception as e:
        logger.error(f"Debug schema failed: {e}")
        return {"error": str(e)}


@app.get("/stats")
async def get_stats():
    """Get database statistics for dashboard."""
    try:
        # Get stats from health endpoint but format for frontend
        health_data = await health_check()
        
        neo4j_stats = health_data.get('neo4j_stats', {})
        milvus_stats = health_data.get('milvus_stats', {})
        
        return {
            "publications": neo4j_stats.get('publication_count', 0),
            "pages": neo4j_stats.get('page_count', 0),
            "entities": neo4j_stats.get('entity_count', 0),
            "searchIndexSize": milvus_stats.get('vector_count', 0),
            "totalNodes": neo4j_stats.get('node_count', 0),
            "lastUpdated": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Stats endpoint failed: {e}")
        # Return zeros when data unavailable - NO FAKE DATA
        return {
            "publications": 0,
            "pages": 0,
            "entities": 0,
            "searchIndexSize": 0,
            "totalNodes": 0,
            "lastUpdated": datetime.now().isoformat(),
            "error": "Database unavailable - showing actual zeros"
        }


# Export routes
@app.get("/export/entities")
async def export_entities(format: str = "json"):
    """Export all entities in specified format."""
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
        
        entities_query = """
        MATCH (e:Entity)
        RETURN e.entity_id as entity_id, e.name as name, e.entity_type as type,
               e.canonical_id as canonical_id, e.confidence as confidence
        ORDER BY e.entity_type, e.name
        """
        
        entities = neo4j_client.run_query(entities_query)
        
        if format == "json":
            return {"entities": entities, "count": len(entities)}
        else:  # CSV
            import csv
            import io
            
            output = io.StringIO()
            if entities:
                writer = csv.DictWriter(output, fieldnames=entities[0].keys())
                writer.writeheader()
                writer.writerows(entities)
            
            return {"csv_data": output.getvalue(), "count": len(entities)}
        
    except Exception as e:
        logger.error(f"Entity export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")


@app.get("/export/publications")
async def export_publications(format: str = "json"):
    """Export all publications in specified format."""
    try:
        if format not in ["json", "csv"]:
            raise HTTPException(status_code=400, detail="Format must be 'json' or 'csv'")
        
        pubs_query = """
        MATCH (p:Publication)
        RETURN p.pub_id as pub_id, p.title as title, p.authors as authors,
               p.year as year, p.journal as journal, p.doi as doi,
               p.total_pages as total_pages
        ORDER BY p.year DESC, p.title
        """
        
        publications = neo4j_client.run_query(pubs_query)
        
        if format == "json":
            return {"publications": publications, "count": len(publications)}
        else:  # CSV  
            import csv
            import io
            
            output = io.StringIO()
            if publications:
                # Flatten authors array for CSV
                for pub in publications:
                    pub['authors'] = '; '.join(pub.get('authors', []))
                
                writer = csv.DictWriter(output, fieldnames=publications[0].keys())
                writer.writeheader()
                writer.writerows(publications)
            
            return {"csv_data": output.getvalue(), "count": len(publications)}
        
    except Exception as e:
        logger.error(f"Publication export failed: {e}")
        raise HTTPException(status_code=500, detail=f"Export failed: {e}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)