from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging

from ..schemas import KGQuery, KGQueryResponse, Publication
from ..services.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/query", response_model=KGQueryResponse)
async def execute_cypher_query(
    cypher_query: str,
    parameters: Optional[str] = None
):
    """
    Execute raw Cypher query against the knowledge graph.
    For advanced users who want to write custom queries.
    """
    try:
        import json
        import time
        
        start_time = time.time()
        
        # Parse parameters if provided
        params = {}
        if parameters:
            try:
                params = json.loads(parameters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid JSON parameters")
        
        # Execute query with safety limits
        if not _is_safe_query(cypher_query):
            raise HTTPException(
                status_code=400, 
                detail="Query contains potentially unsafe operations"
            )
        
        # Add LIMIT if not present (safety measure)
        if "LIMIT" not in cypher_query.upper() and "CREATE" not in cypher_query.upper():
            cypher_query += " LIMIT 1000"
        
        results = neo4j_client.run_query(cypher_query, params)
        
        execution_time = (time.time() - start_time) * 1000
        
        return KGQueryResponse(
            results=results,
            execution_time_ms=execution_time
        )
        
    except Exception as e:
        logger.error(f"Cypher query execution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Query failed: {e}")


@router.get("/visualization")
async def get_graph_visualization(
    entity_types: Optional[List[str]] = None,
    limit: int = 100
):
    """
    Get knowledge graph data optimized for visualization.
    Returns nodes and edges in format suitable for Cytoscape.js
    """
    try:
        graph_data = neo4j_client.get_knowledge_graph_data(entity_types, limit)
        
        # Format for Cytoscape.js
        cytoscape_data = []
        
        # Add nodes
        for node in graph_data['nodes']:
            cytoscape_data.append({
                'data': {
                    'id': node['id'],
                    'label': node['name'],
                    'type': node['type']
                },
                'group': 'nodes',
                'classes': node['type'].lower()
            })
        
        # Add edges
        for relationship in graph_data['relationships']:
            cytoscape_data.append({
                'data': {
                    'id': f"{relationship['source']}-{relationship['target']}",
                    'source': relationship['source'],
                    'target': relationship['target'],
                    'label': relationship['relationship'],
                    'confidence': relationship.get('confidence', 1.0)
                },
                'group': 'edges',
                'classes': relationship['relationship'].lower()
            })
        
        return {
            'elements': cytoscape_data,
            'stats': {
                'nodes': len(graph_data['nodes']),
                'edges': len(graph_data['relationships'])
            }
        }
        
    except Exception as e:
        logger.error(f"Graph visualization data retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Visualization failed: {e}")


@router.get("/entity/{entity_id}")
async def get_entity_details(entity_id: str):
    """Get detailed information about a specific entity."""
    try:
        # Get entity details
        entity_query = """
        MATCH (e:Entity {entity_id: $entity_id})
        RETURN e
        """
        
        entity_result = neo4j_client.run_query(entity_query, {"entity_id": entity_id})
        
        if not entity_result:
            raise HTTPException(status_code=404, detail="Entity not found")
        
        entity = entity_result[0]['e']
        
        # Get related entities
        relations_query = """
        MATCH (e:Entity {entity_id: $entity_id})-[r]-(related:Entity)
        RETURN related, type(r) as relationship, r.confidence as confidence
        LIMIT 20
        """
        
        relations = neo4j_client.run_query(relations_query, {"entity_id": entity_id})
        
        # Get publications mentioning this entity
        publications = neo4j_client.get_entity_publications(entity_id)
        
        return {
            'entity': entity,
            'related_entities': relations,
            'publications': publications,
            'total_mentions': len(publications)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entity details retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Entity retrieval failed: {e}")


@router.get("/path")
async def find_shortest_path(
    source_entity_id: str,
    target_entity_id: str,
    max_hops: int = 5
):
    """Find shortest path between two entities in the knowledge graph."""
    try:
        path_query = """
        MATCH path = shortestPath(
            (source:Entity {entity_id: $source_id})-[*1..{max_hops}]-(target:Entity {entity_id: $target_id})
        )
        RETURN path
        LIMIT 1
        """.format(max_hops=max_hops)
        
        result = neo4j_client.run_query(path_query, {
            "source_id": source_entity_id,
            "target_id": target_entity_id
        })
        
        if not result:
            return {
                'path_found': False,
                'message': f'No path found between entities within {max_hops} hops'
            }
        
        # Format path for visualization
        path_data = result[0]['path']
        
        return {
            'path_found': True,
            'path_length': len(path_data.relationships),
            'path_data': path_data
        }
        
    except Exception as e:
        logger.error(f"Path finding failed: {e}")
        raise HTTPException(status_code=500, detail=f"Path finding failed: {e}")


@router.get("/clusters")
async def get_entity_clusters(
    entity_type: Optional[str] = None,
    min_cluster_size: int = 3
):
    """
    Get entity clusters based on co-occurrence in publications.
    Useful for identifying research themes and related concepts.
    """
    try:
        cluster_query = """
        MATCH (e1:Entity)-[:MENTIONED_IN]->(p:Page)<-[:MENTIONED_IN]-(e2:Entity)
        WHERE e1.entity_id < e2.entity_id  // Avoid duplicate pairs
        {entity_filter}
        WITH e1, e2, count(DISTINCT p) as co_occurrences
        WHERE co_occurrences >= $min_cluster_size
        RETURN e1.entity_id as entity1, e1.name as name1, e1.entity_type as type1,
               e2.entity_id as entity2, e2.name as name2, e2.entity_type as type2,
               co_occurrences
        ORDER BY co_occurrences DESC
        LIMIT 100
        """
        
        entity_filter = ""
        params = {"min_cluster_size": min_cluster_size}
        
        if entity_type:
            entity_filter = "AND e1.entity_type = $entity_type AND e2.entity_type = $entity_type"
            params["entity_type"] = entity_type
        
        final_query = cluster_query.format(entity_filter=entity_filter)
        
        results = neo4j_client.run_query(final_query, params)
        
        # Build clusters using simple graph clustering
        clusters = _build_clusters(results)
        
        return {
            'clusters': clusters,
            'total_clusters': len(clusters),
            'total_pairs': len(results)
        }
        
    except Exception as e:
        logger.error(f"Clustering failed: {e}")
        raise HTTPException(status_code=500, detail=f"Clustering failed: {e}")


@router.get("/statistics")
async def get_graph_statistics():
    """Get comprehensive knowledge graph statistics."""
    try:
        stats_queries = {
            'node_counts': """
            MATCH (n)
            RETURN labels(n) as label, count(n) as count
            ORDER BY count DESC
            """,
            
            'relationship_counts': """
            MATCH ()-[r]->()
            RETURN type(r) as relationship, count(r) as count
            ORDER BY count DESC
            """,
            
            'entity_type_counts': """
            MATCH (e:Entity)
            RETURN e.entity_type as entity_type, count(e) as count
            ORDER BY count DESC
            """,
            
            'connectivity': """
            MATCH (e:Entity)
            OPTIONAL MATCH (e)-[r]-()
            WITH e, count(r) as degree
            RETURN 
                avg(degree) as avg_degree,
                max(degree) as max_degree,
                min(degree) as min_degree,
                percentileCont(degree, 0.5) as median_degree
            """
        }
        
        statistics = {}
        
        for stat_name, query in stats_queries.items():
            try:
                results = neo4j_client.run_query(query)
                statistics[stat_name] = results
            except Exception as e:
                logger.warning(f"Failed to get {stat_name}: {e}")
                statistics[stat_name] = []
        
        return {
            'graph_statistics': statistics,
            'generated_at': '2024-01-01T00:00:00Z'  # Would use actual timestamp
        }
        
    except Exception as e:
        logger.error(f"Statistics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Statistics failed: {e}")


def _is_safe_query(cypher_query: str) -> bool:
    """Check if Cypher query is safe to execute."""
    unsafe_keywords = [
        'DELETE', 'REMOVE', 'SET', 'CREATE', 'MERGE', 
        'DROP', 'DETACH', 'CALL', 'LOAD'
    ]
    
    query_upper = cypher_query.upper()
    
    for keyword in unsafe_keywords:
        if keyword in query_upper:
            return False
    
    return True


def _build_clusters(co_occurrence_data: List[Dict]) -> List[Dict]:
    """Build entity clusters from co-occurrence data."""
    # Simple clustering based on connected components
    from collections import defaultdict
    
    graph = defaultdict(set)
    entities = {}
    
    # Build adjacency graph
    for item in co_occurrence_data:
        e1, e2 = item['entity1'], item['entity2']
        graph[e1].add(e2)
        graph[e2].add(e1)
        entities[e1] = {'name': item['name1'], 'type': item['type1']}
        entities[e2] = {'name': item['name2'], 'type': item['type2']}
    
    # Find connected components
    visited = set()
    clusters = []
    
    for entity_id in graph:
        if entity_id not in visited:
            cluster = []
            stack = [entity_id]
            
            while stack:
                current = stack.pop()
                if current not in visited:
                    visited.add(current)
                    cluster.append({
                        'entity_id': current,
                        'name': entities[current]['name'],
                        'type': entities[current]['type']
                    })
                    stack.extend(graph[current] - visited)
            
            if len(cluster) > 1:  # Only include clusters with multiple entities
                clusters.append({
                    'cluster_id': len(clusters),
                    'entities': cluster,
                    'size': len(cluster)
                })
    
    return sorted(clusters, key=lambda x: x['size'], reverse=True)