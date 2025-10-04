from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
import time

from ..schemas import (
    SemanticSearchRequest, SemanticSearchResponse, SearchResult,
    Publication, Page
)
from ..services.colpali import colpali_service, vector_search_service
from ..services.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(request: SemanticSearchRequest):
    """
    Perform semantic search across all documents.
    Returns ranked pages with similarity scores and snippets.
    """
    try:
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = colpali_service.encode_query(request.query)
        
        # Perform vector search
        search_results = vector_search_service.search(
            query_embedding, 
            top_k=request.top_k
        )
        
        # Convert to response format
        results = []
        for result in search_results:
            search_result = SearchResult(
                page_id=result['page_id'],
                pub_id=result['pub_id'],
                title=result['title'],
                authors=result['authors'],
                score=result['score'],
                snippet=result['snippet'],
                page_number=result['page_number'],
                confidence=min(result['score'], 1.0)  # Normalize confidence
            )
            results.append(search_result)
        
        # Apply filters if provided
        if request.filters:
            results = _apply_filters(results, request.filters)
        
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return SemanticSearchResponse(
            results=results,
            total_results=len(results),
            query_time_ms=query_time
        )
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@router.get("/boolean")
async def boolean_search(
    query: str,
    entity_types: Optional[List[str]] = Query(None),
    year_min: Optional[int] = Query(None),
    year_max: Optional[int] = Query(None),
    top_k: int = Query(10, ge=1, le=100)
):
    """
    Perform boolean/keyword search using Neo4j text matching.
    """
    try:
        # Build Cypher query
        where_clauses = []
        params = {"query": query, "top_k": top_k}
        
        # Add filters
        if entity_types:
            where_clauses.append("e.entity_type IN $entity_types")
            params["entity_types"] = entity_types
            
        if year_min is not None:
            where_clauses.append("p.year >= $year_min")
            params["year_min"] = year_min
            
        if year_max is not None:
            where_clauses.append("p.year <= $year_max")
            params["year_max"] = year_max
        
        where_clause = ""
        if where_clauses:
            where_clause = f"AND {' AND '.join(where_clauses)}"
        
        cypher_query = f"""
        MATCH (pg:Page)-[:PART_OF]->(p:Publication)
        WHERE pg.ocr_text CONTAINS $query
        {where_clause}
        OPTIONAL MATCH (e:Entity)-[:MENTIONED_IN]->(pg)
        RETURN DISTINCT 
            pg.page_id as page_id,
            pg.pub_id as pub_id,
            p.title as title,
            p.authors as authors,
            pg.page_number as page_number,
            pg.ocr_text as text,
            1.0 as score
        ORDER BY p.year DESC
        LIMIT $top_k
        """
        
        results = neo4j_client.run_query(cypher_query, params)
        
        # Format results
        formatted_results = []
        for result in results:
            # Extract snippet around query
            text = result['text']
            query_pos = text.lower().find(query.lower())
            
            if query_pos != -1:
                start = max(0, query_pos - 100)
                end = min(len(text), query_pos + len(query) + 100)
                snippet = text[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
            else:
                snippet = text[:200] + "..." if len(text) > 200 else text
            
            search_result = SearchResult(
                page_id=result['page_id'],
                pub_id=result['pub_id'],
                title=result['title'],
                authors=result['authors'],
                score=result['score'],
                snippet=snippet,
                page_number=result['page_number'],
                confidence=result['score']
            )
            formatted_results.append(search_result)
        
        return SemanticSearchResponse(
            results=formatted_results,
            total_results=len(formatted_results),
            query_time_ms=0.0  # Would measure in production
        )
        
    except Exception as e:
        logger.error(f"Boolean search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {e}")


@router.get("/suggestions")
async def get_search_suggestions(query: str, limit: int = Query(5, ge=1, le=20)):
    """
    Get search suggestions based on entities and publication titles.
    """
    try:
        # Get entity suggestions
        entity_query = """
        MATCH (e:Entity)
        WHERE toLower(e.name) CONTAINS toLower($query)
        RETURN DISTINCT e.name as suggestion, e.entity_type as type
        ORDER BY e.name
        LIMIT $limit
        """
        
        entity_results = neo4j_client.run_query(
            entity_query, 
            {"query": query, "limit": limit // 2}
        )
        
        # Get publication title suggestions
        pub_query = """
        MATCH (p:Publication)
        WHERE toLower(p.title) CONTAINS toLower($query)
        RETURN DISTINCT p.title as suggestion, 'Publication' as type
        ORDER BY p.title
        LIMIT $limit
        """
        
        pub_results = neo4j_client.run_query(
            pub_query, 
            {"query": query, "limit": limit // 2}
        )
        
        # Combine and format suggestions
        suggestions = []
        
        for result in entity_results + pub_results:
            suggestions.append({
                "text": result['suggestion'],
                "type": result['type'],
                "score": 1.0  # Would calculate relevance score in production
            })
        
        return {
            "suggestions": suggestions[:limit],
            "query": query
        }
        
    except Exception as e:
        logger.error(f"Suggestion generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Suggestions failed: {e}")


def _apply_filters(results: List[SearchResult], filters) -> List[SearchResult]:
    """Apply search filters to results."""
    filtered_results = results
    
    # Year range filter
    if filters.year_range:
        min_year, max_year = filters.year_range
        # Would need to join with publication year data
        pass
    
    # Entity type filters
    if filters.organisms or filters.endpoints:
        # Would filter based on page entities
        pass
    
    return filtered_results


@router.get("/filters")
async def get_available_filters():
    """
    Get available filter options (organisms, endpoints, years, etc.).
    """
    try:
        # Get organism options
        organisms_query = """
        MATCH (e:Entity {entity_type: 'Organism'})
        RETURN DISTINCT e.name as name, count(*) as count
        ORDER BY count DESC
        LIMIT 50
        """
        organisms = neo4j_client.run_query(organisms_query)
        
        # Get endpoint options  
        endpoints_query = """
        MATCH (e:Entity {entity_type: 'Endpoint'})
        RETURN DISTINCT e.name as name, count(*) as count
        ORDER BY count DESC
        LIMIT 50
        """
        endpoints = neo4j_client.run_query(endpoints_query)
        
        # Get year range
        year_query = """
        MATCH (p:Publication)
        WHERE p.year IS NOT NULL
        RETURN min(p.year) as min_year, max(p.year) as max_year
        """
        year_result = neo4j_client.run_query(year_query)
        year_range = year_result[0] if year_result else {"min_year": 2000, "max_year": 2024}
        
        return {
            "organisms": [{"name": r['name'], "count": r['count']} for r in organisms],
            "endpoints": [{"name": r['name'], "count": r['count']} for r in endpoints],
            "year_range": [year_range['min_year'], year_range['max_year']],
            "platforms": [],  # Would populate from data
            "funding_sources": []  # Would populate from data
        }
        
    except Exception as e:
        logger.error(f"Filter options retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Filter retrieval failed: {e}")


@router.get("/stats")
async def get_search_stats():
    """Get search and dataset statistics."""
    try:
        stats_query = """
        MATCH (p:Publication)
        OPTIONAL MATCH (pg:Page)-[:PART_OF]->(p)
        OPTIONAL MATCH (e:Entity)
        RETURN 
            count(DISTINCT p) as publications,
            count(DISTINCT pg) as pages,
            count(DISTINCT e) as entities
        """
        
        result = neo4j_client.run_query(stats_query)
        stats = result[0] if result else {"publications": 0, "pages": 0, "entities": 0}
        
        return {
            "total_publications": stats['publications'],
            "total_pages": stats['pages'],
            "total_entities": stats['entities'],
            "search_index_size": vector_search_service.index.ntotal if vector_search_service.index else 0
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        return {
            "total_publications": 0,
            "total_pages": 0,
            "total_entities": 0,
            "search_index_size": 0
        }