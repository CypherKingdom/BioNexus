from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any, Optional
import logging

from ..schemas import KGQuery, KGQueryResponse, Publication
from ..services.neo4j_client import neo4j_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/explore/filtered")
async def explore_graph_filtered(
    node_types: str = None,
    relationship_types: str = None,
    min_connections: int = 0,
    limit: int = 50
):
    """
    Get filtered nodes and relationships for graph exploration.
    Supports advanced filtering by node types, relationship types, and connectivity.
    """
    try:
        # Parse comma-separated filter parameters
        node_type_list = [t.strip() for t in node_types.split(',')] if node_types else []
        rel_type_list = [t.strip() for t in relationship_types.split(',')] if relationship_types else []
        
        # Build dynamic query based on filters
        node_filter = ""
        if node_type_list:
            labels = " OR ".join([f"n:{label}" for label in node_type_list])
            node_filter = f"WHERE {labels}"
        else:
            node_filter = "WHERE n:Publication OR n:Entity OR n:Page"
        
        # Get nodes with connectivity filtering
        if min_connections > 0:
            nodes_query = f"""
            MATCH (n)-[r]-()
            {node_filter}
            WITH n, count(r) as connections
            WHERE connections >= $min_connections
            RETURN 
                id(n) as id,
                labels(n)[0] as type,
                CASE 
                    WHEN n:Publication THEN n.title
                    WHEN n:Entity THEN n.name
                    WHEN n:Page THEN 'Page ' + toString(n.page_number)
                    ELSE 'Unknown'
                END as label,
                properties(n) as properties,
                connections
            ORDER BY connections DESC
            LIMIT $limit
            """
        else:
            nodes_query = f"""
            MATCH (n)
            {node_filter}
            RETURN 
                id(n) as id,
                labels(n)[0] as type,
                CASE 
                    WHEN n:Publication THEN n.title
                    WHEN n:Entity THEN n.name
                    WHEN n:Page THEN 'Page ' + toString(n.page_number)
                    ELSE 'Unknown'
                END as label,
                properties(n) as properties
            LIMIT $limit
            """
        
        nodes_result = neo4j_client.run_query(nodes_query, {
            "min_connections": min_connections,
            "limit": limit
        })
        
        # Get node IDs for relationship filtering
        node_ids = [str(node["id"]) for node in nodes_result]
        
        # Build relationship query with filtering
        rel_filter = ""
        if rel_type_list:
            rel_filter = f"AND type(r) IN {rel_type_list}"
        
        relationships_query = f"""
        MATCH (n)-[r]->(m)
        WHERE id(n) IN $node_ids AND id(m) IN $node_ids {rel_filter}
        RETURN 
            id(n) as source,
            id(m) as target,
            type(r) as type,
            properties(r) as properties
        LIMIT $limit
        """
        
        relationships_result = neo4j_client.run_query(relationships_query, {
            "node_ids": [int(nid) for nid in node_ids],
            "limit": limit
        })
        
        # Process results with same cleaning logic as original
        nodes = []
        for node_data in nodes_result:
            raw_properties = node_data["properties"] or {}
            clean_properties = {}
            
            for key, value in raw_properties.items():
                try:
                    if value is None:
                        clean_properties[key] = "N/A"
                    elif isinstance(value, str):
                        clean_properties[key] = value
                    elif isinstance(value, (int, float, bool)):
                        clean_properties[key] = str(value)
                    elif isinstance(value, list):
                        clean_properties[key] = ", ".join(str(item) for item in value if item is not None)
                    else:
                        clean_properties[key] = str(value)
                except Exception:
                    clean_properties[key] = "Invalid data"
            
            nodes.append({
                "id": str(node_data["id"]),
                "label": node_data["label"] or "Unknown",
                "type": node_data["type"] or "Unknown",
                "properties": clean_properties,
                "connections": node_data.get("connections", 0)
            })
        
        edges = []
        for rel_data in relationships_result:
            raw_properties = rel_data["properties"] or {}
            clean_properties = {}
            
            for key, value in raw_properties.items():
                try:
                    if value is None:
                        clean_properties[key] = "N/A"
                    elif isinstance(value, str):
                        clean_properties[key] = value
                    elif isinstance(value, (int, float, bool)):
                        clean_properties[key] = str(value)
                    else:
                        clean_properties[key] = str(value)
                except Exception:
                    clean_properties[key] = "Invalid data"
            
            edges.append({
                "source": str(rel_data["source"]),
                "target": str(rel_data["target"]),
                "type": rel_data["type"] or "RELATED",
                "properties": clean_properties
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "filters_applied": {
                    "node_types": node_type_list,
                    "relationship_types": rel_type_list,
                    "min_connections": min_connections
                },
                "query_time_ms": 0.0
            }
        }
        
    except Exception as e:
        logger.error(f"Filtered graph exploration failed: {e}")
        return {"nodes": [], "edges": [], "error": str(e)}


@router.get("/explore")
async def explore_graph(limit: int = 50):
    """
    Get nodes and relationships for graph exploration.
    Returns data suitable for visualization.
    """
    try:
        # Get nodes with their basic info - only real data from Neo4j
        nodes_query = """
        MATCH (n)
        WHERE n:Publication OR n:Entity OR n:Page
        RETURN 
            id(n) as id,
            labels(n)[0] as type,
            CASE 
                WHEN n:Publication THEN n.title
                WHEN n:Entity THEN n.name
                WHEN n:Page THEN 'Page ' + toString(n.page_number)
                ELSE 'Unknown'
            END as label,
            properties(n) as properties
        LIMIT $limit
        """
        
        nodes_result = neo4j_client.run_query(nodes_query, {"limit": limit})
        
        # Get relationships between these nodes
        relationships_query = """
        MATCH (n)-[r]->(m)
        WHERE (n:Publication OR n:Entity OR n:Page) AND (m:Publication OR m:Entity OR m:Page)
        RETURN 
            id(n) as source,
            id(m) as target,
            type(r) as type,
            properties(r) as properties
        LIMIT $limit
        """
        
        relationships_result = neo4j_client.run_query(relationships_query, {"limit": limit})
        
        # Process nodes
        nodes = []
        for node_data in nodes_result:
            # Clean properties to ensure they're serializable as strings
            raw_properties = node_data["properties"] or {}
            clean_properties = {}
            
            for key, value in raw_properties.items():
                try:
                    if value is None:
                        clean_properties[key] = "N/A"
                    elif isinstance(value, str):
                        clean_properties[key] = value
                    elif isinstance(value, (int, float, bool)):
                        clean_properties[key] = str(value)
                    elif isinstance(value, list):
                        # Convert list items to strings
                        clean_properties[key] = ", ".join(str(item) for item in value if item is not None)
                    else:
                        # Convert other types to string
                        clean_properties[key] = str(value)
                except Exception:
                    clean_properties[key] = "Invalid data"
            
            nodes.append({
                "id": str(node_data["id"]),
                "label": node_data["label"] or "Unknown",
                "type": node_data["type"] or "Unknown",
                "properties": clean_properties
            })
        
        # Process relationships
        edges = []
        for rel_data in relationships_result:
            # Clean relationship properties too
            raw_properties = rel_data["properties"] or {}
            clean_properties = {}
            
            for key, value in raw_properties.items():
                try:
                    if value is None:
                        clean_properties[key] = "N/A"
                    elif isinstance(value, str):
                        clean_properties[key] = value
                    elif isinstance(value, (int, float, bool)):
                        clean_properties[key] = str(value)
                    else:
                        clean_properties[key] = str(value)
                except Exception:
                    clean_properties[key] = "Invalid data"
            
            edges.append({
                "source": str(rel_data["source"]),
                "target": str(rel_data["target"]),
                "type": rel_data["type"] or "RELATED",
                "properties": clean_properties
            })
        
        return {
            "nodes": nodes,
            "edges": edges,
            "metadata": {
                "total_nodes": len(nodes),
                "total_edges": len(edges),
                "query_time_ms": 0.0  # Would measure in production
            }
        }
        
    except Exception as e:
        logger.error(f"Graph exploration failed: {e}")
        return {"nodes": [], "edges": [], "error": str(e)}


@router.get("/search")
async def search_graph(query: str, limit: int = 30):
    """
    Search for nodes in the knowledge graph by name/title.
    """
    try:
        # Search across different node types
        search_query = """
        MATCH (n)
        WHERE (n:Publication AND toLower(n.title) CONTAINS toLower($query))
           OR (n:Entity AND toLower(n.name) CONTAINS toLower($query))
           OR (n:Page AND toLower(n.text) CONTAINS toLower($query))
        WITH n
        MATCH (n)-[r]-(connected)
        RETURN 
            id(n) as id,
            labels(n)[0] as type,
            CASE 
                WHEN n:Publication THEN n.title
                WHEN n:Entity THEN n.name
                WHEN n:Page THEN 'Page ' + toString(n.page_number)
                ELSE 'Unknown'
            END as label,
            properties(n) as properties,
            id(connected) as connected_id,
            labels(connected)[0] as connected_type,
            type(r) as relationship_type
        LIMIT $limit
        """
        
        search_result = neo4j_client.run_query(search_query, {"query": query, "limit": limit})
        
        # Process results to get unique nodes and relationships
        nodes = {}
        relationships = []
        
        for result in search_result:
            # Add main node
            node_id = str(result["id"])
            if node_id not in nodes:
                # Clean properties for this node too
                raw_properties = result["properties"] or {}
                clean_properties = {}
                
                for key, value in raw_properties.items():
                    try:
                        if value is None:
                            clean_properties[key] = "N/A"
                        elif isinstance(value, str):
                            clean_properties[key] = value
                        elif isinstance(value, (int, float, bool)):
                            clean_properties[key] = str(value)
                        elif isinstance(value, list):
                            clean_properties[key] = ", ".join(str(item) for item in value if item is not None)
                        else:
                            clean_properties[key] = str(value)
                    except Exception:
                        clean_properties[key] = "Invalid data"
                
                nodes[node_id] = {
                    "id": node_id,
                    "label": result["label"] or "Unknown",
                    "type": result["type"],
                    "properties": clean_properties
                }
            
            # Add connected node
            connected_id = str(result["connected_id"])
            if connected_id not in nodes:
                nodes[connected_id] = {
                    "id": connected_id,
                    "label": "Connected Node",
                    "type": result["connected_type"],
                    "properties": {}
                }
            
            # Add relationship
            relationships.append({
                "source": node_id,
                "target": connected_id,
                "type": result["relationship_type"],
                "properties": {}
            })
        
        return {
            "nodes": list(nodes.values()),
            "relationships": relationships
        }
        
    except Exception as e:
        logger.error(f"Graph search failed: {e}")
        return {"nodes": [], "relationships": []}


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


@router.get("/filter-options")
async def get_filter_options():
    """Get available options for filtering the knowledge graph."""
    try:
        # Get all available node types
        node_types_query = """
        MATCH (n)
        WHERE n:Publication OR n:Entity OR n:Page
        RETURN DISTINCT labels(n)[0] as node_type, count(n) as count
        ORDER BY count DESC
        """
        
        # Get all available relationship types
        rel_types_query = """
        MATCH ()-[r]->()
        RETURN DISTINCT type(r) as relationship_type, count(r) as count
        ORDER BY count DESC
        """
        
        # Get connectivity statistics
        connectivity_query = """
        MATCH (n)
        WHERE n:Publication OR n:Entity OR n:Page
        OPTIONAL MATCH (n)-[r]-()
        WITH n, count(r) as connections
        RETURN 
            min(connections) as min_connections,
            max(connections) as max_connections,
            avg(connections) as avg_connections,
            percentileCont(connections, 0.5) as median_connections
        """
        
        node_types_result = neo4j_client.run_query(node_types_query)
        rel_types_result = neo4j_client.run_query(rel_types_query)
        connectivity_result = neo4j_client.run_query(connectivity_query)
        
        return {
            "node_types": [
                {
                    "type": result["node_type"],
                    "count": result["count"]
                }
                for result in node_types_result
            ],
            "relationship_types": [
                {
                    "type": result["relationship_type"],
                    "count": result["count"]
                }
                for result in rel_types_result
            ],
            "connectivity_stats": connectivity_result[0] if connectivity_result else {
                "min_connections": 0,
                "max_connections": 0,
                "avg_connections": 0,
                "median_connections": 0
            }
        }
        
    except Exception as e:
        logger.error(f"Filter options retrieval failed: {e}")
        return {
            "node_types": [],
            "relationship_types": [],
            "connectivity_stats": {
                "min_connections": 0,
                "max_connections": 0,
                "avg_connections": 0,
                "median_connections": 0
            }
        }


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