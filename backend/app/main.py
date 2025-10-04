from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
import logging
import os

from .config import settings
from .logging_config import setup_logging, get_logger
from .exceptions import (
    BioNexusException, 
    bionexus_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    general_exception_handler
)
from .routers import ingest, search, graph, summarize, integrations, mission, export
from .services.neo4j_client import neo4j_client
from .services.milvus_client import milvus_client
from .services.gcs_client import storage_client

# Setup logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="BioNexus API",
    description="AI-powered knowledge graph platform for NASA bioscience publications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(BioNexusException, bionexus_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Mount static files for images
static_dir = "/tmp/bionexus"
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)

app.mount("/images", StaticFiles(directory=static_dir), name="images")

# Include routers
app.include_router(ingest.router, prefix="/ingest", tags=["ingestion"])
app.include_router(search.router, prefix="/search", tags=["search"])
app.include_router(graph.router, prefix="/kg", tags=["knowledge-graph"])
app.include_router(summarize.router, prefix="/summarize", tags=["summarization"])
app.include_router(integrations.router, prefix="/integrations", tags=["external-integrations"])
app.include_router(mission.router, prefix="/mission", tags=["mission-planning"])
app.include_router(export.router, prefix="/export", tags=["data-export"])


@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup."""
    try:
        logger.info("Starting BioNexus API...")
        
        # Initialize Neo4j Aura constraints
        neo4j_client.create_constraints()
        logger.info("Neo4j Aura constraints initialized")
        
        # Initialize Milvus Cloud connection
        milvus_client.connect()
        logger.info("Milvus Cloud connection initialized")
        
        # Initialize Google Cloud Storage
        logger.info("Google Cloud Storage initialized")
        
        logger.info("BioNexus API startup complete")
        
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
        "name": "BioNexus API",
        "version": "1.0.0",
        "description": "AI-powered knowledge graph platform for NASA bioscience publications",
        "endpoints": {
            "ingestion": "/ingest/*",
            "search": "/search/*", 
            "knowledge_graph": "/kg/*",
            "summarization": "/summarize/*",
            "integrations": "/integrations/*",
            "mission_planning": "/mission/*",
            "data_export": "/export/*",
            "documentation": "/docs"
        },
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test Neo4j connection
        neo4j_result = neo4j_client.run_query("RETURN 1 as test")
        neo4j_status = "healthy" if neo4j_result else "unhealthy"
        
        return {
            "status": "healthy",
            "services": {
                "neo4j": neo4j_status,
                "api": "healthy"
            },
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": "2024-01-01T00:00:00Z"
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