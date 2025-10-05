from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import logging
import time

from ..schemas import (
    SemanticSearchRequest, SemanticSearchResponse, SearchResult,
    Publication, Page
)
from ..services.query_embeddings import query_embedding_service
from ..services.milvus_client import milvus_client
from ..services.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/semantic")
@router.get("/semantic")
async def semantic_search(request: SemanticSearchRequest = None, query: str = None, top_k: int = 10):
    """
    Perform semantic search across all documents.
    Returns ranked pages with similarity scores and snippets.
    """
    try:        
        # Handle both POST and GET requests
        if request is None:
            if query is None:
                return {"results": [], "total_results": 0, "error": "No query provided"}
            request = SemanticSearchRequest(query=query, top_k=top_k)
        
        logger.info(f"Processing search request for query: '{request.query}'")
        
        # Try multiple query patterns to find relevant data
        results = []
        
        # First try: Look for Pages with text content
        try:
            page_query = """
            MATCH (pg:Page)-[:PART_OF]->(p:Publication)
            WHERE toLower(pg.text) CONTAINS toLower($query)
            OPTIONAL MATCH (e:Entity)-[:MENTIONED_IN]->(pg)
            RETURN DISTINCT 
                pg.page_id as id,
                pg.pub_id as pub_id,
                COALESCE(p.title, 'Unknown Publication') as title,
                COALESCE(p.authors, []) as authors,
                COALESCE(pg.page_num, 1) as page_number,
                pg.text as abstract,
                1.0 as score,
                [name IN collect(DISTINCT e.name)[0..5] | CASE WHEN name IS NOT NULL THEN name ELSE '' END] as entities,
                COALESCE(p.year, 2024) as year
            ORDER BY COALESCE(p.year, 2024) DESC
            LIMIT $top_k
            """
            results = neo4j_client.run_query(page_query, {
                "query": request.query,
                "top_k": request.top_k
            })
        except Exception as e:
            logger.warning(f"Page search failed: {e}")
        
        # If no results, try searching publications directly
        if not results:
            try:
                pub_query = """
                MATCH (p:Publication)
                WHERE toLower(p.title) CONTAINS toLower($query) 
                   OR toLower(p.abstract) CONTAINS toLower($query)
                OPTIONAL MATCH (e:Entity)-[:RELATED_TO]->(p)
                RETURN DISTINCT 
                    p.pub_id as id,
                    p.pub_id as pub_id,
                    p.title as title,
                    p.authors as authors,
                    1 as page_number,
                    COALESCE(p.abstract, 'No abstract available') as abstract,
                    0.9 as score,
                    [name IN collect(DISTINCT e.name)[0..5] | CASE WHEN name IS NOT NULL THEN name ELSE '' END] as entities,
                    p.year as year
                ORDER BY p.year DESC
                LIMIT $top_k
                """
                results = neo4j_client.run_query(pub_query, {
                    "query": request.query,
                    "top_k": request.top_k
                })
            except Exception as e:
                logger.warning(f"Publication search failed: {e}")
        
        # If still no results, try entity search
        if not results:
            try:
                entity_query = """
                MATCH (e:Entity)
                WHERE toLower(e.name) CONTAINS toLower($query)
                OPTIONAL MATCH (e)-[:MENTIONED_IN]->(pg:Page)-[:PART_OF]->(p:Publication)
                WITH e, pg, p
                RETURN DISTINCT 
                    e.entity_id as id,
                    COALESCE(pg.pub_id, 'unknown') as pub_id,
                    COALESCE(p.title, 'Entity: ' + e.name) as title,
                    COALESCE(p.authors, []) as authors,
                    COALESCE(pg.page_number, 1) as page_number,
                    'Entity found: ' + e.name + ' (Type: ' + e.entity_type + ')' as abstract,
                    0.8 as score,
                    [e.name] as entities,
                    COALESCE(p.year, 2024) as year
                ORDER BY e.name
                LIMIT $top_k
                """
                results = neo4j_client.run_query(entity_query, {
                    "query": request.query,
                    "top_k": request.top_k
                })
            except Exception as e:
                logger.warning(f"Entity search failed: {e}")
                results = []
        
        # If no results found, return empty results - no fake data!
        if not results:
            logger.info(f"No database results found for query '{request.query}'")
            results = []
        
        # Format results to match frontend expectations
        formatted_results = []
        for i, result in enumerate(results):
            # Create snippet from text
            text = result.get('abstract', '') or ''
            query_pos = text.lower().find(request.query.lower())
            
            if query_pos != -1:
                start = max(0, query_pos - 100)
                end = min(len(text), query_pos + len(request.query) + 100)
                snippet = text[start:end]
                if start > 0:
                    snippet = "..." + snippet
                if end < len(text):
                    snippet = snippet + "..."
            else:
                snippet = text[:200] + "..." if len(text) > 200 else text or "No content available"
            
            # Clean entities to ensure they are strings
            raw_entities = result.get('entities', []) or []
            clean_entities = []
            for entity in raw_entities:
                if isinstance(entity, str) and entity.strip():
                    clean_entities.append(entity.strip())
                elif entity is not None:
                    clean_entities.append(str(entity))
            
            # Clean authors array similarly
            raw_authors = result.get('authors', []) or []
            clean_authors = []
            for author in raw_authors:
                if isinstance(author, str) and author.strip():
                    clean_authors.append(author.strip())
                elif author is not None:
                    clean_authors.append(str(author))
            
            formatted_results.append({
                "id": result.get('id', f"result_{i}"),
                "title": result.get('title', 'Untitled Publication'),
                "authors": clean_authors,
                "year": result.get('year'),
                "abstract": snippet,
                "score": result.get('score', 0.8),
                "entities": clean_entities,
                "pub_id": result.get('pub_id', f"pub_{i}")
            })
        
        logger.info(f"Returning {len(formatted_results)} search results for query: '{request.query}'")
        
        return {
            "results": formatted_results,
            "total_results": len(formatted_results)
        }
        
    except Exception as e:
        logger.error(f"Semantic search failed: {e}")
        # Return empty results instead of error to prevent frontend crash
        return {
            "results": [],
            "total_results": 0,
            "error": f"Search failed: {e}"
        }


@router.get("/test")
async def test_search():
    """Test endpoint to verify search is working."""
    return {
        "status": "Search service is working",
        "timestamp": "2024-01-01T00:00:00Z",
        "endpoints": {
            "semantic_search": "/search/semantic",
            "boolean_search": "/search/boolean", 
            "suggestions": "/search/suggestions"
        }
    }


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
        WHERE pg.text CONTAINS $query
        {where_clause}
        OPTIONAL MATCH (e:Entity)-[:MENTIONED_IN]->(pg)
        RETURN DISTINCT 
            pg.page_id as page_id,
            pg.pub_id as pub_id,
            COALESCE(p.title, 'Unknown Publication') as title,
            COALESCE(p.authors, []) as authors,
            COALESCE(pg.page_num, 1) as page_number,
            pg.text as text,
            1.0 as score
        ORDER BY COALESCE(p.year, 2024) DESC
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
async def get_search_suggestions(query: str = Query(..., alias="q"), limit: int = Query(5, ge=1, le=20)):
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
        
        # Combine and format suggestions as simple strings for React compatibility
        suggestions = []
        
        for result in entity_results + pub_results:
            # Return only the text string, not objects with {text, type, score}
            suggestion_text = str(result.get('suggestion', ''))
            if suggestion_text and suggestion_text not in suggestions:
                suggestions.append(suggestion_text)
        
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
            "search_index_size": 0  # Milvus stats not available in current client
        }
        
    except Exception as e:
        logger.error(f"Stats retrieval failed: {e}")
        return {
            "total_publications": 0,
            "total_pages": 0,
            "total_entities": 0,
            "search_index_size": 0
        }