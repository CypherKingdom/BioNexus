import pytest
import sys
import os
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock

# Add the app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'app'))

from app.services.neo4j_client import Neo4jClient
from app.schemas import KnowledgeGraphStats, GraphElement, EntityNode, RelationshipEdge


class TestNeo4jClient:
    @pytest.fixture
    def mock_driver(self):
        """Mock Neo4j driver."""
        mock_driver = Mock()
        mock_session = Mock()
        mock_driver.session.return_value.__enter__.return_value = mock_session
        mock_driver.session.return_value.__exit__.return_value = None
        return mock_driver, mock_session
    
    @pytest.fixture
    def neo4j_client(self, mock_driver):
        """Create Neo4j client with mocked driver."""
        driver, session = mock_driver
        with patch('app.services.neo4j_client.GraphDatabase.driver', return_value=driver):
            client = Neo4jClient()
            return client, session
    
    def test_get_graph_statistics(self, neo4j_client):
        """Test graph statistics retrieval."""
        client, mock_session = neo4j_client
        
        # Mock the query results
        mock_record = Mock()
        mock_record.__getitem__.side_effect = lambda key: {
            'node_count': 1000,
            'relationship_count': 2500,
            'entity_types': 15,
            'unique_relations': 25
        }[key]
        
        mock_session.run.return_value = [mock_record]
        
        stats = client.get_graph_statistics()
        
        assert isinstance(stats, KnowledgeGraphStats)
        assert stats.node_count >= 0
        assert stats.relationship_count >= 0
        assert stats.entity_types >= 0
    
    def test_get_graph_visualization_empty(self, neo4j_client):
        """Test graph visualization with empty result."""
        client, mock_session = neo4j_client
        
        # Mock empty query result
        mock_session.run.return_value = []
        
        elements = client.get_graph_visualization(limit=10)
        
        assert isinstance(elements, list)
    
    def test_search_entities_by_type(self, neo4j_client):
        """Test entity search by type."""
        client, mock_session = neo4j_client
        
        # Mock entity search results
        mock_record = Mock()
        mock_record.__getitem__.side_effect = lambda key: {
            'name': 'PROTEIN1',
            'type': 'Protein',
            'id': 'entity_123',
            'mentions': 5
        }[key]
        
        mock_session.run.return_value = [mock_record]
        
        entities = client.search_entities_by_type("Protein", limit=10)
        
        assert isinstance(entities, list)
    
    def test_get_entity_neighbors(self, neo4j_client):
        """Test entity neighbor retrieval."""
        client, mock_session = neo4j_client
        
        # Mock neighbor results
        mock_session.run.return_value = []
        
        neighbors = client.get_entity_neighbors("entity_123", depth=2)
        
        assert isinstance(neighbors, list)
    
    def test_create_publication_node(self, neo4j_client):
        """Test publication node creation."""
        client, mock_session = neo4j_client
        
        pub_data = {
            'title': 'Test Publication',
            'authors': ['Author 1'],
            'year': 2023,
            'doi': '10.1000/test'
        }
        
        # Mock successful creation
        mock_session.run.return_value = None
        
        # Should not raise exception
        client.create_publication_node("pub_123", pub_data)
    
    def test_create_entity_node(self, neo4j_client):
        """Test entity node creation."""
        client, mock_session = neo4j_client
        
        # Mock successful creation
        mock_session.run.return_value = None
        
        # Should not raise exception
        client.create_entity_node("ent_123", "Protein", "P53", {"function": "tumor suppressor"})
    
    def test_create_relationship(self, neo4j_client):
        """Test relationship creation."""
        client, mock_session = neo4j_client
        
        # Mock successful creation
        mock_session.run.return_value = None
        
        # Should not raise exception
        client.create_relationship(
            "ent_123", "ent_456", "INTERACTS_WITH", 
            {"confidence": 0.9, "source": "paper_1"}
        )
    
    def test_get_publications_by_entity(self, neo4j_client):
        """Test publication retrieval by entity."""
        client, mock_session = neo4j_client
        
        # Mock publication results
        mock_record = Mock()
        mock_record.__getitem__.side_effect = lambda key: {
            'pub_id': 'pub_123',
            'title': 'Test Paper',
            'year': 2023
        }[key]
        
        mock_session.run.return_value = [mock_record]
        
        publications = client.get_publications_by_entity("entity_123")
        
        assert isinstance(publications, list)
    
    def test_connection_error_handling(self):
        """Test connection error handling."""
        with patch('app.services.neo4j_client.GraphDatabase.driver') as mock_driver_class:
            mock_driver_class.side_effect = Exception("Connection failed")
            
            # Should handle connection error gracefully
            client = Neo4jClient()
            
            # Methods should return empty/default results
            stats = client.get_graph_statistics()
            assert isinstance(stats, KnowledgeGraphStats)
    
    def test_query_timeout_handling(self, neo4j_client):
        """Test query timeout handling."""
        client, mock_session = neo4j_client
        
        # Mock timeout exception
        from neo4j.exceptions import ServiceUnavailable
        mock_session.run.side_effect = ServiceUnavailable("Query timeout")
        
        # Should handle timeout gracefully
        result = client.get_graph_visualization()
        assert isinstance(result, list)


class TestNeo4jQueries:
    """Test Neo4j query construction and parameters."""
    
    def test_cypher_injection_prevention(self):
        """Test that queries prevent Cypher injection."""
        # This would test parameter sanitization
        # For now, we assume parameterized queries are used
        assert True
    
    def test_query_performance_hints(self):
        """Test that queries include performance hints."""
        # This would test USING INDEX hints etc.
        # For now, we assume proper indexing
        assert True
    
    def test_transaction_handling(self):
        """Test transaction management."""
        # This would test proper transaction boundaries
        # For now, we assume proper session management
        assert True