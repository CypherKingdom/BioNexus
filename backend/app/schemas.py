from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class IngestMode(str, Enum):
    SAMPLE = "sample"
    FULL = "full"


class IngestStatus(BaseModel):
    job_id: str
    status: str  # "running", "completed", "failed", "pending"
    mode: IngestMode
    progress: float = Field(ge=0.0, le=1.0)
    total_documents: int = 0
    processed_documents: int = 0
    failed_documents: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None


class SearchFilters(BaseModel):
    year_range: Optional[tuple[int, int]] = None
    organisms: Optional[List[str]] = None
    endpoints: Optional[List[str]] = None
    platforms: Optional[List[str]] = None
    funding_sources: Optional[List[str]] = None


class SemanticSearchRequest(BaseModel):
    query: str
    filters: Optional[SearchFilters] = None
    top_k: int = Field(default=10, ge=1, le=100)


class SearchResult(BaseModel):
    page_id: str
    pub_id: str
    title: str
    authors: List[str]
    score: float = Field(ge=0.0, le=1.0)
    snippet: str
    page_number: int
    confidence: float = Field(ge=0.0, le=1.0)


class SemanticSearchResponse(BaseModel):
    results: List[SearchResult]
    total_results: int
    query_time_ms: float


class Publication(BaseModel):
    pub_id: str
    title: str
    authors: List[str]
    abstract: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    funding_sources: List[str] = []
    total_pages: int = 0
    created_at: datetime
    updated_at: datetime


class Page(BaseModel):
    page_id: str
    pub_id: str
    page_number: int
    ocr_text: str
    image_url: Optional[str] = None
    embedding: Optional[List[float]] = None
    extracted_figures: List[str] = []
    extracted_tables: List[str] = []


class Entity(BaseModel):
    entity_id: str
    name: str
    entity_type: str  # "Organism", "Endpoint", "Instrument", "Dataset", "Grant"
    canonical_id: Optional[str] = None  # NCBI, UniProt, etc.
    confidence: float = Field(ge=0.0, le=1.0)
    mentions: List[Dict[str, Any]] = []


class Relationship(BaseModel):
    source_entity_id: str
    target_entity_id: str
    relationship_type: str
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: List[str] = []


class RAGRequest(BaseModel):
    question: str
    pub_ids: Optional[List[str]] = None
    top_k_pages: Optional[int] = Field(default=5, ge=1, le=20)
    include_context: bool = True


class Citation(BaseModel):
    citation_id: int
    pub_id: str
    page_id: str
    snippet: str
    confidence: float = Field(ge=0.0, le=1.0)


class RAGResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: float = Field(ge=0.0, le=1.0)
    insufficient_evidence: bool = False
    candidate_sources: List[str] = []


class KGQuery(BaseModel):
    cypher_query: str
    parameters: Optional[Dict[str, Any]] = {}


class KGQueryResponse(BaseModel):
    results: List[Dict[str, Any]]
    execution_time_ms: float


class ExportFormat(str, Enum):
    CSV = "csv"
    JSON = "json"
    CYPHER = "cypher"


class ExportRequest(BaseModel):
    format: ExportFormat
    entity_types: Optional[List[str]] = None
    relationship_types: Optional[List[str]] = None
    pub_ids: Optional[List[str]] = None


class MissionConstraint(BaseModel):
    duration_days: Optional[int] = None
    radiation_level: Optional[str] = None  # "low", "moderate", "high"
    gravity_level: Optional[str] = None  # "zero", "partial", "full"
    temperature_range: Optional[tuple[float, float]] = None


class MissionPlannerRequest(BaseModel):
    constraints: MissionConstraint
    research_goals: List[str] = []


class MissionRecommendation(BaseModel):
    recommendation: str
    confidence: float = Field(ge=0.0, le=1.0)
    supporting_evidence: List[Citation]
    risk_level: str  # "low", "moderate", "high"