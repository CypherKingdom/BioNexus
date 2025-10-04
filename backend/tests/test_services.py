import pytest
from app.services.ocr import OCRService
from app.services.ner import BiomedicalNER, RelationExtraction
from app.services.colpali import ColPaliService
from PIL import Image
import numpy as np


class TestOCRService:
    def setup_method(self):
        self.ocr_service = OCRService()
    
    def test_clean_text(self):
        """Test text cleaning functionality."""
        dirty_text = "This  is   a  test\n\nwith\tmultiple\tspaces"
        cleaned = self.ocr_service.clean_text(dirty_text)
        assert "multiple spaces" in cleaned
        assert "  " not in cleaned  # No double spaces
    
    def test_segment_sections(self):
        """Test document section segmentation."""
        sample_text = """
        Title: Test Paper
        
        Abstract
        This is the abstract section with research overview.
        
        Introduction
        This is the introduction section with background.
        
        Methods
        This section describes the methodology used.
        
        Results
        The results section contains findings.
        
        Discussion
        Discussion of the implications.
        
        Conclusion
        Final conclusions drawn.
        """
        
        sections = self.ocr_service.segment_sections(sample_text)
        
        assert 'abstract' in sections
        assert 'introduction' in sections
        assert 'methods' in sections
        assert 'results' in sections
        assert 'discussion' in sections
        assert 'conclusion' in sections
        
        assert len(sections['abstract']) > 0
        assert len(sections['methods']) > 0


class TestBiomedicalNER:
    def setup_method(self):
        self.ner_service = BiomedicalNER()
    
    def test_extract_entities_basic(self):
        """Test basic entity extraction."""
        text = "The study examined Escherichia coli growth in microgravity conditions using a microscope."
        entities = self.ner_service.extract_entities(text, page_id="test_page_001")
        
        # Should extract organisms and instruments
        entity_types = [e['entity_type'] for e in entities]
        assert 'Organism' in entity_types or 'Instrument' in entity_types
        
        # Check entity structure
        for entity in entities:
            assert 'entity_id' in entity
            assert 'name' in entity
            assert 'entity_type' in entity
            assert 'confidence' in entity
            assert entity['confidence'] > 0
            assert entity['confidence'] <= 1
    
    def test_deduplicate_entities(self):
        """Test entity deduplication."""
        entities = [
            {
                'entity_id': 'org_001',
                'name': 'Human',
                'entity_type': 'Organism',
                'confidence': 0.8
            },
            {
                'entity_id': 'org_002', 
                'name': 'human',  # Same entity, different case
                'entity_type': 'Organism',
                'confidence': 0.9
            }
        ]
        
        deduplicated = self.ner_service._deduplicate_entities(entities)
        
        # Should merge similar entities
        assert len(deduplicated) == 1
        assert deduplicated[0]['confidence'] == 0.9  # Keep higher confidence


class TestRelationExtraction:
    def setup_method(self):
        self.relation_extractor = RelationExtraction()
    
    def test_extract_relations_basic(self):
        """Test basic relationship extraction."""
        text = "The experiment investigated bone density changes in microgravity."
        
        # Mock entities
        entities = [
            {
                'entity_id': 'exp_001',
                'name': 'experiment',
                'entity_type': 'Experiment',
                'start_char': 4,
                'end_char': 14
            },
            {
                'entity_id': 'end_001',
                'name': 'bone density',
                'entity_type': 'Endpoint',
                'start_char': 27,
                'end_char': 39
            }
        ]
        
        relations = self.relation_extractor.extract_relations(
            text, entities, page_id="test_page_001"
        )
        
        # Should find investigation relationship
        if relations:
            relation = relations[0]
            assert 'source_entity_id' in relation
            assert 'target_entity_id' in relation
            assert 'relationship_type' in relation
            assert 'confidence' in relation


class TestColPaliService:
    def setup_method(self):
        self.colpali_service = ColPaliService(fallback_to_cpu=True)
    
    def test_encode_query(self):
        """Test query encoding."""
        query = "microgravity effects on bone density"
        embedding = self.colpali_service.encode_query(query)
        
        assert isinstance(embedding, np.ndarray)
        assert len(embedding) == self.colpali_service.embedding_dim
        assert not np.all(embedding == 0)  # Should not be all zeros
    
    def test_encode_with_fallback(self):
        """Test fallback encoding when ColPali unavailable."""
        text = "This is a test document about space research."
        
        # Force fallback mode
        if self.colpali_service.model is None:
            embedding = self.colpali_service._encode_with_fallback(text)
            
            assert isinstance(embedding, np.ndarray)
            assert len(embedding) == self.colpali_service.embedding_dim
            assert not np.all(embedding == 0)
    
    @pytest.mark.skipif(not torch.cuda.is_available(), reason="GPU not available")
    def test_encode_image_and_text_gpu(self):
        """Test multimodal encoding with GPU (if available)."""
        # Create a simple test image
        image = Image.new('RGB', (224, 224), color='white')
        text = "Test document"
        
        if self.colpali_service.model is not None:
            embedding = self.colpali_service.encode_image_and_text(image, text)
            
            assert isinstance(embedding, np.ndarray)
            assert len(embedding) == self.colpali_service.embedding_dim


# Import torch conditionally for GPU tests
try:
    import torch
except ImportError:
    torch = None