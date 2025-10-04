import os
from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging

from ..config import settings

logger = logging.getLogger(__name__)


class Neo4jClient:
    def __init__(self):
        self.uri = settings.neo4j_uri
        self.user = settings.neo4j_user
        self.password = settings.neo4j_password
        self.driver = None
        self.connect()

    def connect(self):
        """Establish connection to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri, 
                auth=(self.user, self.password)
            )
            logger.info("Connected to Neo4j database")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    def close(self):
        """Close the connection to Neo4j."""
        if self.driver:
            self.driver.close()

    def run_query(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Run a Cypher query and return results."""
        if not self.driver:
            raise Exception("Neo4j driver not initialized")
        
        try:
            with self.driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def create_constraints(self):
        """Create database constraints and indexes."""
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Publication) REQUIRE p.pub_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (pg:Page) REQUIRE pg.page_id IS UNIQUE", 
            "CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (exp:Experiment) REQUIRE exp.experiment_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (d:Dataset) REQUIRE d.dataset_id IS UNIQUE",
            "CREATE INDEX IF NOT EXISTS FOR (p:Publication) ON (p.year)",
            "CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.entity_type)",
            "CREATE INDEX IF NOT EXISTS FOR (pg:Page) ON (pg.page_number)"
        ]
        
        for constraint in constraints:
            try:
                self.run_query(constraint)
                logger.info(f"Applied constraint: {constraint}")
            except Exception as e:
                logger.warning(f"Failed to apply constraint {constraint}: {e}")

    def create_publication(self, pub_data: Dict[str, Any]) -> str:
        """Create a publication node."""
        query = """
        CREATE (p:Publication {
            pub_id: $pub_id,
            title: $title,
            authors: $authors,
            abstract: $abstract,
            year: $year,
            journal: $journal,
            doi: $doi,
            funding_sources: $funding_sources,
            total_pages: $total_pages,
            created_at: datetime(),
            updated_at: datetime()
        })
        RETURN p.pub_id as pub_id
        """
        result = self.run_query(query, pub_data)
        return result[0]["pub_id"] if result else None

    def create_page(self, page_data: Dict[str, Any]) -> str:
        """Create a page node and link it to publication."""
        query = """
        MATCH (p:Publication {pub_id: $pub_id})
        CREATE (pg:Page {
            page_id: $page_id,
            pub_id: $pub_id,
            page_number: $page_number,
            ocr_text: $ocr_text,
            image_url: $image_url,
            embedding: $embedding,
            extracted_figures: $extracted_figures,
            extracted_tables: $extracted_tables
        })
        CREATE (pg)-[:PART_OF]->(p)
        RETURN pg.page_id as page_id
        """
        result = self.run_query(query, page_data)
        return result[0]["page_id"] if result else None

    def create_entity(self, entity_data: Dict[str, Any]) -> str:
        """Create an entity node."""
        query = """
        MERGE (e:Entity {entity_id: $entity_id})
        ON CREATE SET 
            e.name = $name,
            e.entity_type = $entity_type,
            e.canonical_id = $canonical_id,
            e.confidence = $confidence,
            e.mentions = $mentions,
            e.created_at = datetime()
        ON MATCH SET
            e.updated_at = datetime(),
            e.mentions = e.mentions + $mentions
        RETURN e.entity_id as entity_id
        """
        result = self.run_query(query, entity_data)
        return result[0]["entity_id"] if result else None

    def create_relationship(self, rel_data: Dict[str, Any]):
        """Create a relationship between entities."""
        query = f"""
        MATCH (source:Entity {{entity_id: $source_entity_id}})
        MATCH (target:Entity {{entity_id: $target_entity_id}})
        CREATE (source)-[:{rel_data['relationship_type']} {{
            confidence: $confidence,
            evidence: $evidence,
            created_at: datetime()
        }}]->(target)
        """
        self.run_query(query, rel_data)

    def semantic_search_pages(self, embedding: List[float], top_k: int = 10) -> List[Dict[str, Any]]:
        """Find pages similar to the given embedding using cosine similarity."""
        # This is a simplified version - in production you'd use vector index
        query = """
        MATCH (pg:Page)-[:PART_OF]->(p:Publication)
        WHERE pg.embedding IS NOT NULL
        WITH pg, p,
             reduce(dot = 0.0, i IN range(0, size($embedding)-1) | 
                dot + ($embedding[i] * pg.embedding[i])) as dot_product,
             sqrt(reduce(norm_a = 0.0, i IN range(0, size($embedding)-1) | 
                norm_a + ($embedding[i] * $embedding[i]))) as norm_a,
             sqrt(reduce(norm_b = 0.0, i IN range(0, size(pg.embedding)-1) | 
                norm_b + (pg.embedding[i] * pg.embedding[i]))) as norm_b
        WITH pg, p, dot_product / (norm_a * norm_b) as similarity
        WHERE similarity > 0.1
        RETURN pg.page_id as page_id, pg.pub_id as pub_id, p.title as title,
               p.authors as authors, similarity as score, pg.ocr_text as snippet,
               pg.page_number as page_number
        ORDER BY similarity DESC
        LIMIT $top_k
        """
        return self.run_query(query, {"embedding": embedding, "top_k": top_k})

    def get_publication(self, pub_id: str) -> Optional[Dict[str, Any]]:
        """Get publication details with pages."""
        query = """
        MATCH (p:Publication {pub_id: $pub_id})
        OPTIONAL MATCH (pg:Page)-[:PART_OF]->(p)
        RETURN p, collect(pg) as pages
        """
        result = self.run_query(query, {"pub_id": pub_id})
        return result[0] if result else None

    def get_knowledge_graph_data(self, entity_types: List[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Get knowledge graph nodes and relationships for visualization."""
        entity_filter = ""
        if entity_types:
            entity_filter = f"WHERE e.entity_type IN {entity_types}"
            
        nodes_query = f"""
        MATCH (e:Entity)
        {entity_filter}
        RETURN e.entity_id as id, e.name as name, e.entity_type as type
        LIMIT $limit
        """
        
        relationships_query = """
        MATCH (source:Entity)-[r]->(target:Entity)
        WHERE source.entity_id IN $entity_ids AND target.entity_id IN $entity_ids
        RETURN source.entity_id as source, target.entity_id as target, 
               type(r) as relationship, r.confidence as confidence
        """
        
        nodes = self.run_query(nodes_query, {"limit": limit})
        entity_ids = [node["id"] for node in nodes]
        relationships = self.run_query(relationships_query, {"entity_ids": entity_ids})
        
        return {
            "nodes": nodes,
            "relationships": relationships
        }

    def get_entity_publications(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get publications that mention a specific entity."""
        query = """
        MATCH (e:Entity {entity_id: $entity_id})-[:MENTIONED_IN]->(pg:Page)-[:PART_OF]->(p:Publication)
        RETURN DISTINCT p.pub_id as pub_id, p.title as title, p.authors as authors, p.year as year
        ORDER BY p.year DESC
        """
        return self.run_query(query, {"entity_id": entity_id})


# Global client instance
neo4j_client = Neo4jClient()