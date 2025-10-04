// Neo4j Database Setup and Constraints
// This script sets up the BioNexus knowledge graph schema

// Create constraints for unique identifiers
CREATE CONSTRAINT IF NOT EXISTS FOR (p:Publication) REQUIRE p.pub_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (pg:Page) REQUIRE pg.page_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (e:Entity) REQUIRE e.entity_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (exp:Experiment) REQUIRE exp.experiment_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (o:Organism) REQUIRE o.organism_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (ep:Endpoint) REQUIRE ep.endpoint_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (i:Instrument) REQUIRE i.instrument_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (d:Dataset) REQUIRE d.dataset_id IS UNIQUE;
CREATE CONSTRAINT IF NOT EXISTS FOR (g:Grant) REQUIRE g.grant_id IS UNIQUE;

// Create indexes for better query performance
CREATE INDEX IF NOT EXISTS FOR (p:Publication) ON (p.year);
CREATE INDEX IF NOT EXISTS FOR (p:Publication) ON (p.title);
CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.entity_type);
CREATE INDEX IF NOT EXISTS FOR (e:Entity) ON (e.name);
CREATE INDEX IF NOT EXISTS FOR (pg:Page) ON (pg.page_number);
CREATE INDEX IF NOT EXISTS FOR (exp:Experiment) ON (exp.experiment_type);

// Create full-text search indexes
CREATE FULLTEXT INDEX IF NOT EXISTS publicationFulltext FOR (n:Publication) ON EACH [n.title, n.abstract];
CREATE FULLTEXT INDEX IF NOT EXISTS pageFulltext FOR (n:Page) ON EACH [n.ocr_text];
CREATE FULLTEXT INDEX IF NOT EXISTS entityFulltext FOR (n:Entity) ON EACH [n.name];

// Sample data insertion for demo purposes
// Publications
MERGE (p1:Publication {
  pub_id: 'pub_sample_001',
  title: 'Effects of Microgravity on Bone Density in Long-Duration Spaceflight',
  authors: ['Johnson, M.', 'Smith, K.', 'Williams, R.'],
  abstract: 'This study examines the impact of prolonged microgravity exposure on bone mineral density in astronauts during missions lasting 6+ months.',
  year: 2023,
  journal: 'Space Medicine & Biology',
  doi: '10.1000/sample.2023.001',
  funding_sources: ['NASA Life Sciences', 'NIH Space Research'],
  total_pages: 12,
  created_at: datetime(),
  updated_at: datetime()
});

MERGE (p2:Publication {
  pub_id: 'pub_sample_002', 
  title: 'Cardiovascular Adaptation to Partial Gravity Environments',
  authors: ['Davis, L.', 'Thompson, J.', 'Martinez, A.'],
  abstract: 'Investigation of heart rate variability and blood pressure changes in simulated Mars gravity conditions.',
  year: 2023,
  journal: 'Aerospace Medical Research',
  doi: '10.1000/sample.2023.002',
  funding_sources: ['NASA Human Research Program'],
  total_pages: 15,
  created_at: datetime(),
  updated_at: datetime()
});

MERGE (p3:Publication {
  pub_id: 'pub_sample_003',
  title: 'Plant Growth Responses in Controlled Space Environment Systems',
  authors: ['Brown, S.', 'Lee, H.', 'Garcia, M.'],
  abstract: 'Analysis of crop yield and nutritional content in space-based agricultural systems under LED lighting.',
  year: 2024,
  journal: 'Astrobiology & Space Agriculture', 
  doi: '10.1000/sample.2024.001',
  funding_sources: ['NASA Space Technology Mission Directorate'],
  total_pages: 18,
  created_at: datetime(),
  updated_at: datetime()
});

// Sample Pages
MERGE (page1:Page {
  page_id: 'pub_sample_001_page_001',
  pub_id: 'pub_sample_001',
  page_number: 1,
  ocr_text: 'Abstract: This study examines the impact of prolonged microgravity exposure on bone mineral density in astronauts during missions lasting 6+ months. Methods included DXA scans and biochemical markers.',
  image_url: '/images/pub_sample_001/page_001.png',
  extracted_figures: ['Figure 1: Bone density measurements'],
  extracted_tables: ['Table 1: Demographic data']
});

MERGE (page2:Page {
  page_id: 'pub_sample_002_page_001', 
  pub_id: 'pub_sample_002',
  page_number: 1,
  ocr_text: 'Introduction: Cardiovascular deconditioning is a major concern for long-duration spaceflight. This research investigates heart rate variability in partial gravity.',
  image_url: '/images/pub_sample_002/page_001.png',
  extracted_figures: ['Figure 1: ECG monitoring setup'],
  extracted_tables: []
});

// Create page relationships
MATCH (p1:Publication {pub_id: 'pub_sample_001'}), (page1:Page {page_id: 'pub_sample_001_page_001'})
MERGE (page1)-[:PART_OF]->(p1);

MATCH (p2:Publication {pub_id: 'pub_sample_002'}), (page2:Page {page_id: 'pub_sample_002_page_001'})
MERGE (page2)-[:PART_OF]->(p2);

// Sample Entities
MERGE (e1:Entity {
  entity_id: 'organism_human_001',
  name: 'Human',
  entity_type: 'Organism',
  canonical_id: 'NCBITaxon:9606',
  confidence: 0.95,
  mentions: []
});

MERGE (e2:Entity {
  entity_id: 'endpoint_bone_density_001',
  name: 'Bone Density',
  entity_type: 'Endpoint',
  canonical_id: null,
  confidence: 0.90,
  mentions: []
});

MERGE (e3:Entity {
  entity_id: 'endpoint_heart_rate_001',
  name: 'Heart Rate Variability',
  entity_type: 'Endpoint', 
  canonical_id: null,
  confidence: 0.88,
  mentions: []
});

MERGE (e4:Entity {
  entity_id: 'organism_arabidopsis_001',
  name: 'Arabidopsis thaliana',
  entity_type: 'Organism',
  canonical_id: 'NCBITaxon:3702',
  confidence: 0.92,
  mentions: []
});

MERGE (e5:Entity {
  entity_id: 'instrument_dxa_001',
  name: 'DXA Scanner',
  entity_type: 'Instrument',
  canonical_id: null,
  confidence: 0.85,
  mentions: []
});

// Sample Experiments
MERGE (exp1:Experiment {
  experiment_id: 'exp_bone_study_001',
  experiment_type: 'Longitudinal Study',
  duration: '6 months',
  conditions: ['Microgravity', 'ISS Environment'],
  subjects: 12
});

MERGE (exp2:Experiment {
  experiment_id: 'exp_cardio_study_001', 
  experiment_type: 'Simulation Study',
  duration: '30 days',
  conditions: ['Partial Gravity', 'Mars Analog'],
  subjects: 24
});

// Entity relationships to pages
MATCH (e1:Entity {entity_id: 'organism_human_001'}), (page1:Page {page_id: 'pub_sample_001_page_001'})
MERGE (e1)-[:MENTIONED_IN]->(page1);

MATCH (e2:Entity {entity_id: 'endpoint_bone_density_001'}), (page1:Page {page_id: 'pub_sample_001_page_001'})
MERGE (e2)-[:MENTIONED_IN]->(page1);

MATCH (e1:Entity {entity_id: 'organism_human_001'}), (page2:Page {page_id: 'pub_sample_002_page_001'})
MERGE (e1)-[:MENTIONED_IN]->(page2);

MATCH (e3:Entity {entity_id: 'endpoint_heart_rate_001'}), (page2:Page {page_id: 'pub_sample_002_page_001'})
MERGE (e3)-[:MENTIONED_IN]->(page2);

// Experiment relationships
MATCH (exp1:Experiment {experiment_id: 'exp_bone_study_001'}), (p1:Publication {pub_id: 'pub_sample_001'})
MERGE (exp1)-[:DESCRIBED_IN]->(p1);

MATCH (exp1:Experiment {experiment_id: 'exp_bone_study_001'}), (e2:Entity {entity_id: 'endpoint_bone_density_001'})
MERGE (exp1)-[:INVESTIGATES]->(e2);

MATCH (exp2:Experiment {experiment_id: 'exp_cardio_study_001'}), (p2:Publication {pub_id: 'pub_sample_002'}) 
MERGE (exp2)-[:DESCRIBED_IN]->(p2);

// Entity relationships
MATCH (e1:Entity {entity_id: 'organism_human_001'}), (e2:Entity {entity_id: 'endpoint_bone_density_001'})
MERGE (e1)-[:HAS_ENDPOINT {confidence: 0.9, evidence: ['Clinical studies']}]->(e2);

MATCH (e1:Entity {entity_id: 'organism_human_001'}), (e3:Entity {entity_id: 'endpoint_heart_rate_001'})
MERGE (e1)-[:HAS_ENDPOINT {confidence: 0.88, evidence: ['Physiological monitoring']}]->(e3);

MATCH (e5:Entity {entity_id: 'instrument_dxa_001'}), (e2:Entity {entity_id: 'endpoint_bone_density_001'})
MERGE (e5)-[:MEASURES {confidence: 0.95, evidence: ['Standard protocol']}]->(e2);