from fastapi import APIRouter, HTTPException, BackgroundTasks, UploadFile, File, Body
from typing import List
import os
import uuid
import logging
import asyncio
from datetime import datetime
import shutil

from ..schemas import IngestStatus, IngestMode
from ..services.ocr import ocr_service
from ..services.colpali import colpali_service, vector_search_service
from ..services.ner import biomedical_ner, relation_extractor
from ..services.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

router = APIRouter()

# Global job tracking
active_jobs = {}


async def run_ingestion_pipeline(job_id: str, mode: IngestMode, pdf_paths: List[str]):
    """Background task to run the complete ingestion pipeline."""
    try:
        job = active_jobs[job_id]
        job["status"] = "running"
        job["start_time"] = datetime.now()
        
        total_pdfs = len(pdf_paths)
        processed = 0
        failed = 0
        
        for pdf_path in pdf_paths:
            try:
                logger.info(f"Processing PDF: {pdf_path}")
                
                # Generate unique publication ID
                pub_id = f"pub_{uuid.uuid4().hex[:8]}"
                
                # Extract publication metadata from filename/path
                pub_data = {
                    "pub_id": pub_id,
                    "title": os.path.basename(pdf_path).replace('.pdf', ''),
                    "authors": ["Unknown"],  # Would extract from PDF in production
                    "abstract": None,
                    "year": None,
                    "journal": None,
                    "doi": None,
                    "funding_sources": [],
                    "total_pages": 0
                }
                
                # Create output directory for this publication
                output_dir = f"/tmp/bionexus/{pub_id}"
                os.makedirs(output_dir, exist_ok=True)
                
                # OCR Processing
                logger.info(f"Running OCR on {pdf_path}")
                page_results = ocr_service.process_pdf(pdf_path, output_dir)
                
                pub_data["total_pages"] = len(page_results)
                
                # Create publication in Neo4j
                neo4j_client.create_publication(pub_data)
                
                # Process each page
                page_embeddings = []
                page_metadata = []
                
                for page_result in page_results:
                    page_id = f"{pub_id}_page_{page_result['page_number']:03d}"
                    
                    # Extract entities from page text
                    entities = biomedical_ner.extract_entities(
                        page_result['text'], 
                        page_id=page_id
                    )
                    
                    # Canonicalize entities
                    entities = biomedical_ner.canonicalize_entities(entities)
                    
                    # Extract relationships
                    relations = relation_extractor.extract_relations(
                        page_result['text'], 
                        entities, 
                        page_id=page_id
                    )
                    
                    # Generate embeddings
                    try:
                        from PIL import Image
                        if os.path.exists(page_result['image_path']):
                            image = Image.open(page_result['image_path'])
                            embedding = colpali_service.encode_image_and_text(
                                image, page_result['text']
                            )
                        else:
                            embedding = colpali_service.encode_query(page_result['text'])
                    except Exception as e:
                        logger.error(f"Embedding generation failed for page {page_id}: {e}")
                        embedding = None
                    
                    # Create page data
                    page_data = {
                        "page_id": page_id,
                        "pub_id": pub_id,
                        "page_number": page_result['page_number'],
                        "ocr_text": page_result['text'],
                        "image_url": f"/images/{pub_id}/page_{page_result['page_number']:03d}.png",
                        "embedding": embedding.tolist() if embedding is not None else None,
                        "extracted_figures": [f['type'] for f in page_result.get('figures', [])],
                        "extracted_tables": [t['type'] for t in page_result.get('tables', [])]
                    }
                    
                    # Create page in Neo4j
                    neo4j_client.create_page(page_data)
                    
                    # Store for vector search
                    if embedding is not None:
                        page_embeddings.append(embedding)
                        page_metadata.append({
                            'page_id': page_id,
                            'pub_id': pub_id,
                            'title': pub_data['title'],
                            'authors': pub_data['authors'],
                            'page_number': page_result['page_number'],
                            'snippet': page_result['text'][:200] + "..." if len(page_result['text']) > 200 else page_result['text']
                        })
                    
                    # Create entities in Neo4j
                    for entity in entities:
                        neo4j_client.create_entity(entity)
                        
                        # Link entity to page
                        neo4j_client.run_query(
                            """
                            MATCH (e:Entity {entity_id: $entity_id})
                            MATCH (pg:Page {page_id: $page_id})
                            CREATE (e)-[:MENTIONED_IN]->(pg)
                            """,
                            {"entity_id": entity['entity_id'], "page_id": page_id}
                        )
                    
                    # Create relationships in Neo4j
                    for relation in relations:
                        try:
                            neo4j_client.create_relationship(relation)
                        except Exception as e:
                            logger.warning(f"Failed to create relationship: {e}")
                
                # Add embeddings to vector search
                if page_embeddings:
                    vector_search_service.add_embeddings(page_embeddings, page_metadata)
                
                processed += 1
                logger.info(f"Successfully processed {pub_id} ({processed}/{total_pdfs})")
                
            except Exception as e:
                logger.error(f"Failed to process {pdf_path}: {e}")
                failed += 1
            
            # Update job progress
            job["processed_documents"] = processed
            job["failed_documents"] = failed
            job["progress"] = processed / total_pdfs
        
        # Mark job as completed
        job["status"] = "completed"
        job["end_time"] = datetime.now()
        
        logger.info(f"Ingestion completed: {processed} processed, {failed} failed")
        
    except Exception as e:
        logger.error(f"Ingestion pipeline failed: {e}")
        job["status"] = "failed"
        job["error_message"] = str(e)
        job["end_time"] = datetime.now()


@router.post("/upload", response_model=dict)
async def upload_pdf(file: UploadFile = File(...)):
    """Upload a PDF file for processing."""
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="File must be a PDF")
    
    try:
        # Save uploaded file
        upload_dir = "/tmp/bionexus/uploads"
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return {
            "message": "File uploaded successfully",
            "filename": file.filename,
            "path": file_path
        }
        
    except Exception as e:
        logger.error(f"File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.post("/run", response_model=IngestStatus)
async def run_ingestion(
    background_tasks: BackgroundTasks,
    mode: IngestMode = Body("sample")
):
    """
    Start ingestion pipeline for sample or full dataset.
    mode: 'sample' (3 papers) or 'full' (608 papers)
    """
    try:
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Determine PDF paths based on mode
        if mode == IngestMode.SAMPLE:
            pdf_dir = "/run/media/CypherKing/Local Disk/BioNexus/data/sample_papers"
            pdf_paths = [
                os.path.join(pdf_dir, f) 
                for f in os.listdir(pdf_dir) 
                if f.endswith('.pdf')
            ][:3]  # Limit to 3 for sample
        else:  # FULL mode
            pdf_dir = "/data/full_papers"  # Would contain all 608 papers
            pdf_paths = [
                os.path.join(pdf_dir, f) 
                for f in os.listdir(pdf_dir) 
                if f.endswith('.pdf')
            ] if os.path.exists(pdf_dir) else []
        
        if not pdf_paths:
            raise HTTPException(
                status_code=404, 
                detail=f"No PDF files found for mode: {mode}"
            )
        
        # Initialize job status
        job_status = IngestStatus(
            job_id=job_id,
            status="pending",
            mode=mode,
            progress=0.0,
            total_documents=len(pdf_paths),
            processed_documents=0,
            failed_documents=0
        )
        
        active_jobs[job_id] = job_status.dict()
        
        # Start background processing
        background_tasks.add_task(
            run_ingestion_pipeline,
            job_id,
            mode,
            pdf_paths
        )
        
        return job_status
        
    except Exception as e:
        logger.error(f"Failed to start ingestion: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status", response_model=List[IngestStatus])
async def get_ingestion_status():
    """Get status of all ingestion jobs."""
    return [IngestStatus(**job) for job in active_jobs.values()]


@router.get("/status/{job_id}", response_model=IngestStatus)
async def get_job_status(job_id: str):
    """Get status of specific ingestion job."""
    if job_id not in active_jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return IngestStatus(**active_jobs[job_id])