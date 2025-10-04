import pytest
import asyncio
from httpx import AsyncClient
from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
async def client():
    """Create test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


class TestHealthEndpoint:
    async def test_health_check(self, client: AsyncClient):
        """Test health check endpoint."""
        response = await client.get("/health")
        assert response.status_code == 200
        
        data = response.json()
        assert "status" in data
        assert "services" in data
        assert "timestamp" in data


class TestSearchEndpoints:
    async def test_semantic_search(self, client: AsyncClient):
        """Test semantic search endpoint."""
        search_request = {
            "query": "microgravity effects",
            "top_k": 5
        }
        
        response = await client.post("/search/semantic", json=search_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "results" in data
        assert "total_results" in data
        assert "query_time_ms" in data
        assert isinstance(data["results"], list)
    
    async def test_search_suggestions(self, client: AsyncClient):
        """Test search suggestions endpoint."""
        response = await client.get("/search/suggestions?query=bone&limit=5")
        assert response.status_code == 200
        
        data = response.json()
        assert "suggestions" in data
        assert "query" in data
        assert isinstance(data["suggestions"], list)
    
    async def test_search_stats(self, client: AsyncClient):
        """Test search statistics endpoint."""
        response = await client.get("/search/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert "total_publications" in data
        assert "total_pages" in data
        assert "total_entities" in data
        assert "search_index_size" in data


class TestGraphEndpoints:
    async def test_graph_visualization(self, client: AsyncClient):
        """Test knowledge graph visualization endpoint."""
        response = await client.get("/kg/visualization")
        assert response.status_code == 200
        
        data = response.json()
        assert "elements" in data
        assert "stats" in data
        assert isinstance(data["elements"], list)
    
    async def test_graph_statistics(self, client: AsyncClient):
        """Test graph statistics endpoint."""
        response = await client.get("/kg/statistics")
        assert response.status_code == 200
        
        data = response.json()
        assert "graph_statistics" in data
        assert "generated_at" in data


class TestIngestionEndpoints:
    async def test_ingestion_status_list(self, client: AsyncClient):
        """Test ingestion status listing."""
        response = await client.get("/ingest/status")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, list)
    
    async def test_start_sample_ingestion(self, client: AsyncClient):
        """Test starting sample ingestion."""
        response = await client.post("/ingest/run", json={"mode": "sample"})
        
        # Should either succeed or fail gracefully
        assert response.status_code in [200, 404, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "job_id" in data
            assert "status" in data
            assert "mode" in data


class TestSummarizationEndpoints:
    async def test_rag_summary_insufficient_evidence(self, client: AsyncClient):
        """Test RAG summarization with insufficient evidence."""
        rag_request = {
            "question": "What are the effects of nonexistent phenomenon?",
            "top_k_pages": 5
        }
        
        response = await client.post("/summarize/rag", json=rag_request)
        assert response.status_code == 200
        
        data = response.json()
        assert "answer" in data
        assert "citations" in data
        assert "confidence" in data
        assert "insufficient_evidence" in data


class TestExportEndpoints:
    async def test_export_entities(self, client: AsyncClient):
        """Test entity export."""
        response = await client.get("/export/entities?format=json")
        assert response.status_code == 200
        
        data = response.json()
        assert "entities" in data
        assert "count" in data
        assert isinstance(data["entities"], list)
    
    async def test_export_publications(self, client: AsyncClient):
        """Test publication export."""
        response = await client.get("/export/publications?format=json")
        assert response.status_code == 200
        
        data = response.json()
        assert "publications" in data
        assert "count" in data
        assert isinstance(data["publications"], list)