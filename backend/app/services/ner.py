import spacy
from spacy import displacy
from typing import List, Dict, Set, Tuple
import logging
import re
import requests
from collections import defaultdict

logger = logging.getLogger(__name__)


class BiomedicalNER:
    def __init__(self):
        self.nlp = None
        self.entity_types = {
            'SPECIES': 'Organism',
            'CELL': 'Organism', 
            'ORGAN': 'Endpoint',
            'TISSUE': 'Endpoint',
            'PROTEIN': 'Endpoint',
            'GENE': 'Endpoint',
            'CHEMICAL': 'Endpoint',
            'DISEASE': 'Endpoint',
            'EXPERIMENT': 'Experiment',
            'INSTRUMENT': 'Instrument',
            'DATASET': 'Dataset'
        }
        self._load_model()
    
    def _load_model(self):
        """Load the SciSpacy biomedical NER model."""
        try:
            # Load the biomedical NER model
            self.nlp = spacy.load("en_ner_bionlp13cg_md")
            logger.info("Loaded SciSpacy biomedical NER model")
        except OSError as e:
            logger.error(f"Failed to load SciSpacy model: {e}")
            logger.info("Attempting to install model...")
            try:
                import subprocess
                subprocess.check_call([
                    "pip", "install", 
                    "https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_ner_bionlp13cg_md-0.5.3.tar.gz"
                ])
                self.nlp = spacy.load("en_ner_bionlp13cg_md")
                logger.info("Successfully installed and loaded SciSpacy model")
            except Exception as install_error:
                logger.error(f"Failed to install SciSpacy model: {install_error}")
                # Fallback to basic spaCy model
                try:
                    self.nlp = spacy.load("en_core_web_sm")
                    logger.warning("Using fallback en_core_web_sm model")
                except:
                    raise Exception("No spaCy model available")
    
    def extract_entities(self, text: str, page_id: str = None) -> List[Dict]:
        """Extract biomedical entities from text."""
        if not self.nlp:
            return []
        
        entities = []
        
        try:
            # Process text with spaCy
            doc = self.nlp(text)
            
            # Extract named entities
            for ent in doc.ents:
                entity_type = self.entity_types.get(ent.label_, 'Unknown')
                
                # Calculate confidence based on entity characteristics
                confidence = self._calculate_confidence(ent, doc)
                
                entity = {
                    'entity_id': f"{entity_type.lower()}_{hash(ent.text.lower()) % 1000000}",
                    'name': ent.text.strip(),
                    'entity_type': entity_type,
                    'start_char': ent.start_char,
                    'end_char': ent.end_char,
                    'confidence': confidence,
                    'spacy_label': ent.label_,
                    'canonical_id': None,
                    'page_id': page_id
                }
                
                entities.append(entity)
            
            # Add rule-based entities
            rule_entities = self._extract_rule_based_entities(text, page_id)
            entities.extend(rule_entities)
            
            # Remove duplicates and merge similar entities
            entities = self._deduplicate_entities(entities)
            
            logger.info(f"Extracted {len(entities)} entities from text")
            return entities
            
        except Exception as e:
            logger.error(f"Entity extraction failed: {e}")
            return []
    
    def _calculate_confidence(self, ent, doc) -> float:
        """Calculate confidence score for extracted entity."""
        base_confidence = 0.7
        
        # Boost confidence for longer entities
        if len(ent.text) > 10:
            base_confidence += 0.1
        
        # Boost confidence for capitalized entities
        if ent.text[0].isupper():
            base_confidence += 0.05
        
        # Boost confidence for entities with specific patterns
        if re.match(r'^[A-Z][a-z]+\s+[a-z]+$', ent.text):  # Species pattern
            base_confidence += 0.1
        
        return min(base_confidence, 1.0)
    
    def _extract_rule_based_entities(self, text: str, page_id: str = None) -> List[Dict]:
        """Extract entities using rule-based patterns."""
        entities = []
        
        # Organism patterns
        organism_patterns = [
            r'\b[A-Z][a-z]+ [a-z]+\b',  # Species names
            r'\bmice\b|\bmouse\b|\brat\b|\brats\b',  # Common lab animals
            r'\b[Ee]scherichia coli\b|\bE\. coli\b',
            r'\b[Ss]accharomyces cerevisiae\b'
        ]
        
        for pattern in organism_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'entity_id': f"organism_{hash(match.group().lower()) % 1000000}",
                    'name': match.group(),
                    'entity_type': 'Organism',
                    'start_char': match.start(),
                    'end_char': match.end(),
                    'confidence': 0.8,
                    'spacy_label': 'RULE_ORGANISM',
                    'canonical_id': None,
                    'page_id': page_id
                })
        
        # Instrument patterns
        instrument_patterns = [
            r'\bmicroscop[ey]\b',
            r'\bspectromet[ery]\b',
            r'\bcentrifuge\b',
            r'\bPCR\b|\bpolymerase chain reaction\b',
            r'\bfluorescence\b',
            r'\bX-ray\b'
        ]
        
        for pattern in instrument_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'entity_id': f"instrument_{hash(match.group().lower()) % 1000000}",
                    'name': match.group(),
                    'entity_type': 'Instrument',
                    'start_char': match.start(),
                    'end_char': match.end(),
                    'confidence': 0.75,
                    'spacy_label': 'RULE_INSTRUMENT',
                    'canonical_id': None,
                    'page_id': page_id
                })
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """Remove duplicate entities and merge similar ones."""
        seen_entities = {}
        deduplicated = []
        
        for entity in entities:
            # Create a normalized key for deduplication
            key = f"{entity['entity_type']}_{entity['name'].lower().strip()}"
            
            if key not in seen_entities:
                seen_entities[key] = entity
                deduplicated.append(entity)
            else:
                # Merge with existing entity (keep higher confidence)
                existing = seen_entities[key]
                if entity['confidence'] > existing['confidence']:
                    seen_entities[key] = entity
                    # Replace in deduplicated list
                    for i, e in enumerate(deduplicated):
                        if e == existing:
                            deduplicated[i] = entity
                            break
        
        return deduplicated
    
    def canonicalize_entities(self, entities: List[Dict]) -> List[Dict]:
        """Attempt to link entities to external knowledge bases."""
        for entity in entities:
            if entity['entity_type'] == 'Organism':
                canonical_id = self._get_ncbi_taxon_id(entity['name'])
                entity['canonical_id'] = canonical_id
            elif entity['entity_type'] == 'Endpoint' and 'protein' in entity.get('spacy_label', '').lower():
                canonical_id = self._get_uniprot_id(entity['name'])
                entity['canonical_id'] = canonical_id
        
        return entities
    
    def _get_ncbi_taxon_id(self, species_name: str) -> str:
        """Get NCBI Taxonomy ID for species name."""
        try:
            # Simple NCBI Taxonomy lookup (would need API key for production)
            url = f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
            params = {
                'db': 'taxonomy',
                'term': species_name,
                'retmode': 'json'
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'esearchresult' in data and 'idlist' in data['esearchresult']:
                    ids = data['esearchresult']['idlist']
                    if ids:
                        return f"NCBITaxon:{ids[0]}"
            
        except Exception as e:
            logger.debug(f"Failed to get NCBI ID for {species_name}: {e}")
        
        return None
    
    def _get_uniprot_id(self, protein_name: str) -> str:
        """Get UniProt ID for protein name."""
        try:
            # Simple UniProt lookup
            url = f"https://rest.uniprot.org/uniprotkb/search"
            params = {
                'query': protein_name,
                'format': 'json',
                'size': 1
            }
            
            response = requests.get(url, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if 'results' in data and data['results']:
                    return f"UniProt:{data['results'][0]['primaryAccession']}"
            
        except Exception as e:
            logger.debug(f"Failed to get UniProt ID for {protein_name}: {e}")
        
        return None


class RelationExtraction:
    def __init__(self):
        self.relation_patterns = {
            'INVESTIGATED': [
                r'(\w+)\s+(was|were)?\s*(investigated|studied|examined|analyzed)',
                r'(investigation|study|analysis)\s+of\s+(\w+)',
                r'(\w+)\s+(response|effect|impact)\s+on\s+(\w+)'
            ],
            'REPORTS': [
                r'(\w+)\s+(showed|demonstrated|indicated|revealed)\s+(\w+)',
                r'(\w+)\s+(results?|findings?)\s+(suggest|show|indicate)'
            ],
            'DERIVED_FROM': [
                r'(\w+)\s+(derived|obtained|extracted)\s+from\s+(\w+)',
                r'(\w+)\s+(samples?)\s+from\s+(\w+)'
            ],
            'MENTIONS': [
                r'(\w+)\s+(mentioned|discussed|described)\s+(\w+)',
                r'(as\s+reported\s+by|according\s+to)\s+(\w+)'
            ]
        }
    
    def extract_relations(self, text: str, entities: List[Dict], page_id: str = None) -> List[Dict]:
        """Extract relationships between entities."""
        relations = []
        
        # Create entity lookup by position
        entity_positions = {}
        for entity in entities:
            for pos in range(entity['start_char'], entity['end_char']):
                entity_positions[pos] = entity
        
        # Apply rule-based relation extraction
        for relation_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    # Find entities within the match
                    match_entities = []
                    for pos in range(match.start(), match.end()):
                        if pos in entity_positions:
                            entity = entity_positions[pos]
                            if entity not in match_entities:
                                match_entities.append(entity)
                    
                    # Create relations between found entities
                    if len(match_entities) >= 2:
                        for i in range(len(match_entities) - 1):
                            source = match_entities[i]
                            target = match_entities[i + 1]
                            
                            relation = {
                                'source_entity_id': source['entity_id'],
                                'target_entity_id': target['entity_id'],
                                'relationship_type': relation_type,
                                'confidence': 0.7,
                                'evidence': [match.group()],
                                'page_id': page_id
                            }
                            
                            relations.append(relation)
        
        logger.info(f"Extracted {len(relations)} relations from text")
        return relations


# Global service instances
biomedical_ner = BiomedicalNER()
relation_extractor = RelationExtraction()