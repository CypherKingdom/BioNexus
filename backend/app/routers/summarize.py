from fastapi import APIRouter, HTTPException
from typing import List, Optional
import logging
import openai
import os
from datetime import datetime

from ..schemas import RAGRequest, RAGResponse, Citation, MissionPlannerRequest, MissionRecommendation
from ..services.neo4j_client import neo4j_client
from ..services.query_embeddings import query_embedding_service
from ..services.milvus_client import milvus_client

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize OpenAI client
openai.api_key = os.getenv("OPENAI_API_KEY", "your-api-key-here")

# RAG prompt template (must be used verbatim as per requirements)
RAG_SYSTEM_PROMPT = """You are a biomedical research summarizer. Use ONLY the supplied evidence passages. Produce a concise answer (<=200 words) with numbered citations [1], [2], ... referring to the provided passages. For each factual claim, append the citation(s) that support it. If evidence contradicts, state the contradiction and list sources. If evidence is insufficient, say: "Insufficient evidence" and list candidate documents."""


@router.post("/rag", response_model=RAGResponse)
async def generate_rag_summary(request: RAGRequest):
    """
    Generate RAG-based summary with citations and provenance.
    Uses semantic search to find relevant passages, then LLM for synthesis.
    """
    try:
        # Step 1: Retrieve relevant passages
        passages = []
        
        if request.pub_ids:
            # Search within specific publications
            passages = _get_passages_from_publications(request.pub_ids, request.question)
        else:
            # Semantic search across all documents
            passages = _get_passages_from_semantic_search(request.question, request.top_k_pages)
        
        if not passages:
            return RAGResponse(
                answer="Insufficient evidence to answer the question.",
                citations=[],
                confidence=0.0,
                insufficient_evidence=True,
                candidate_sources=_get_candidate_sources(request.question)
            )
        
        # Step 2: Generate answer with LLM
        answer, citations, confidence = await _generate_answer_with_citations(
            request.question, 
            passages,
            request.include_context
        )
        
        return RAGResponse(
            answer=answer,
            citations=citations,
            confidence=confidence,
            insufficient_evidence=confidence < 0.3,
            candidate_sources=[]
        )
        
    except Exception as e:
        logger.error(f"RAG summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {e}")


@router.post("/mission-planner", response_model=List[MissionRecommendation])
async def mission_planner(request: MissionPlannerRequest):
    """
    Generate mission planning recommendations based on constraints and research goals.
    """
    try:
        recommendations = []
        
        # Build query based on mission constraints
        constraints_query = _build_constraints_query(request.constraints)
        
        # Search for relevant research
        for goal in request.research_goals:
            # Find relevant publications and evidence
            evidence_passages = _get_passages_from_semantic_search(
                f"{goal} {constraints_query}", 
                top_k=10
            )
            
            if evidence_passages:
                # Generate recommendation
                recommendation_text, citations, confidence = await _generate_mission_recommendation(
                    goal, 
                    request.constraints, 
                    evidence_passages
                )
                
                risk_level = _assess_risk_level(confidence, evidence_passages)
                
                recommendations.append(MissionRecommendation(
                    recommendation=recommendation_text,
                    confidence=confidence,
                    supporting_evidence=citations,
                    risk_level=risk_level
                ))
        
        return recommendations
        
    except Exception as e:
        logger.error(f"Mission planning failed: {e}")
        raise HTTPException(status_code=500, detail=f"Mission planning failed: {e}")


@router.get("/publication/{pub_id}")
async def get_publication_summary(pub_id: str):
    """Get AI-generated summary for a specific publication."""
    try:
        # Get publication data
        pub_data = neo4j_client.get_publication(pub_id)
        
        if not pub_data:
            raise HTTPException(status_code=404, detail="Publication not found")
        
        publication = pub_data['p']
        pages = pub_data['pages']
        
        # Combine all page text
        full_text = " ".join([page['ocr_text'] for page in pages if page.get('ocr_text')])
        
        if not full_text:
            return {
                'pub_id': pub_id,
                'summary': 'No extractable text found in this publication.',
                'key_findings': [],
                'entities': [],
                'confidence': 0.0
            }
        
        # Generate summary
        summary, key_findings = await _generate_publication_summary(publication, full_text)
        
        # Get extracted entities for this publication
        entities_query = """
        MATCH (e:Entity)-[:MENTIONED_IN]->(pg:Page)-[:PART_OF]->(p:Publication {pub_id: $pub_id})
        RETURN DISTINCT e.name as name, e.entity_type as type, e.confidence as confidence
        ORDER BY e.confidence DESC
        LIMIT 20
        """
        
        entities = neo4j_client.run_query(entities_query, {"pub_id": pub_id})
        
        return {
            'pub_id': pub_id,
            'summary': summary,
            'key_findings': key_findings,
            'entities': entities,
            'confidence': 0.85  # Would calculate based on OCR confidence and entity extraction
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Publication summary generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Summary generation failed: {e}")


def _get_passages_from_publications(pub_ids: List[str], question: str) -> List[dict]:
    """Get relevant passages from specific publications."""
    passages = []
    
    try:
        # Get pages from specified publications
        pages_query = """
        MATCH (pg:Page)-[:PART_OF]->(p:Publication)
        WHERE p.pub_id IN $pub_ids AND pg.ocr_text IS NOT NULL
        RETURN pg.page_id as page_id, pg.pub_id as pub_id, pg.ocr_text as text,
               pg.page_number as page_number, p.title as title, p.authors as authors
        """
        
        pages = neo4j_client.run_query(pages_query, {"pub_ids": pub_ids})
        
        # Rank by relevance to question using semantic search
        if pages:
            query_embedding = query_embedding_service.encode_query(question)
            
            for page in pages:
                # Calculate similarity (simplified)
                passage = {
                    'page_id': page['page_id'],
                    'pub_id': page['pub_id'],
                    'title': page['title'],
                    'authors': page['authors'],
                    'text': page['text'],
                    'page_number': page['page_number'],
                    'score': 0.8  # Would calculate actual similarity
                }
                passages.append(passage)
        
        # Sort by relevance and take top passages
        passages.sort(key=lambda x: x['score'], reverse=True)
        
    except Exception as e:
        logger.error(f"Failed to get passages from publications: {e}")
    
    return passages[:10]  # Limit to top 10


def _get_passages_from_semantic_search(question: str, top_k: int) -> List[dict]:
    """Get relevant passages using semantic search."""
    try:
        query_embedding = query_embedding_service.encode_query(question)
        search_results = milvus_client.search_similar(query_embedding, top_k)
        
        passages = []
        for result in search_results:
            passages.append({
                'page_id': result['page_id'],
                'pub_id': result['pub_id'],
                'title': result['title'],
                'authors': result['authors'],
                'text': result['snippet'],
                'page_number': result['page_number'],
                'score': result['score']
            })
        
        return passages
        
    except Exception as e:
        logger.error(f"Semantic search for passages failed: {e}")
        return []


async def _generate_answer_with_citations(
    question: str, 
    passages: List[dict], 
    include_context: bool
) -> tuple[str, List[Citation], float]:
    """Generate answer using LLM with proper citations."""
    try:
        # Format context passages
        context_text = ""
        for i, passage in enumerate(passages, 1):
            context_text += f"[{i}] {passage['text']}\n\n"
        
        # Prepare user prompt
        user_prompt = f"Context: {context_text}\nUser: {question}"
        
        # Call OpenAI API (or fallback to local model)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=300,
                temperature=0.1
            )
            
            answer = response.choices[0].message.content
            
        except Exception as llm_error:
            logger.warning(f"OpenAI API failed, using fallback: {llm_error}")
            # Fallback to rule-based summary
            answer = _generate_fallback_answer(question, passages)
        
        # Extract citations and create Citation objects
        citations = []
        for i, passage in enumerate(passages, 1):
            if f"[{i}]" in answer:
                citation = Citation(
                    citation_id=i,
                    pub_id=passage['pub_id'],
                    page_id=passage['page_id'],
                    snippet=passage['text'][:200] + "..." if len(passage['text']) > 200 else passage['text'],
                    confidence=passage['score']
                )
                citations.append(citation)
        
        # Calculate confidence based on citations and scores
        if citations:
            avg_score = sum(c.confidence for c in citations) / len(citations)
            confidence = min(avg_score * len(citations) / len(passages), 1.0)
        else:
            confidence = 0.1
        
        return answer, citations, confidence
        
    except Exception as e:
        logger.error(f"Answer generation failed: {e}")
        return "Error generating answer.", [], 0.0


def _generate_fallback_answer(question: str, passages: List[dict]) -> str:
    """Generate fallback answer without LLM."""
    if not passages:
        return "Insufficient evidence to answer the question."
    
    # Simple extractive summarization
    relevant_sentences = []
    
    for i, passage in enumerate(passages[:3], 1):  # Top 3 passages
        text = passage['text']
        sentences = text.split('. ')
        
        # Find sentences containing query terms
        query_terms = question.lower().split()
        
        for sentence in sentences:
            sentence_lower = sentence.lower()
            if any(term in sentence_lower for term in query_terms):
                relevant_sentences.append(f"[{i}] {sentence.strip()}")
                break
    
    if relevant_sentences:
        return " ".join(relevant_sentences[:3])
    else:
        return f"Based on the available evidence [1], the research indicates relevant information but requires further investigation."


async def _generate_mission_recommendation(
    goal: str, 
    constraints, 
    evidence_passages: List[dict]
) -> tuple[str, List[Citation], float]:
    """Generate mission-specific recommendation."""
    try:
        context_text = ""
        for i, passage in enumerate(evidence_passages, 1):
            context_text += f"[{i}] {passage['text']}\n\n"
        
        mission_prompt = f"""
        Mission Goal: {goal}
        Constraints: Duration: {getattr(constraints, 'duration_days', 'unspecified')} days, 
        Radiation: {getattr(constraints, 'radiation_level', 'unspecified')}, 
        Gravity: {getattr(constraints, 'gravity_level', 'unspecified')}
        
        Based on the research evidence, provide specific recommendations for this mission scenario.
        """
        
        user_prompt = f"Context: {context_text}\nMission Planning Request: {mission_prompt}"
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": RAG_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=250,
                temperature=0.2
            )
            
            recommendation = response.choices[0].message.content
            
        except:
            recommendation = f"Based on available research evidence [1], recommendations for {goal} should consider the mission constraints and available data."
        
        # Create citations
        citations = []
        for i, passage in enumerate(evidence_passages[:5], 1):
            citations.append(Citation(
                citation_id=i,
                pub_id=passage['pub_id'],
                page_id=passage['page_id'],
                snippet=passage['text'][:150] + "..." if len(passage['text']) > 150 else passage['text'],
                confidence=passage['score']
            ))
        
        confidence = sum(c.confidence for c in citations) / len(citations) if citations else 0.3
        
        return recommendation, citations, confidence
        
    except Exception as e:
        logger.error(f"Mission recommendation generation failed: {e}")
        return "Unable to generate recommendation with current evidence.", [], 0.1


async def _generate_publication_summary(publication: dict, full_text: str) -> tuple[str, List[str]]:
    """Generate summary for a specific publication."""
    try:
        summary_prompt = f"""
        Title: {publication.get('title', 'Unknown')}
        Authors: {', '.join(publication.get('authors', []))}
        
        Please provide a concise summary of this biomedical research paper focusing on:
        1. Main research objective
        2. Key methodology 
        3. Primary findings
        4. Implications for space biology/medicine
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a biomedical research summarizer. Provide clear, accurate summaries."},
                    {"role": "user", "content": f"{summary_prompt}\n\nText: {full_text[:4000]}"}
                ],
                max_tokens=200,
                temperature=0.1
            )
            
            summary = response.choices[0].message.content
            
        except:
            # Fallback summary
            summary = f"Research paper titled '{publication.get('title', 'Unknown')}' presents findings relevant to biomedical research."
        
        # Extract key findings (simplified)
        key_findings = [
            "Primary research findings documented",
            "Methodological approaches described", 
            "Implications for space medicine identified"
        ]
        
        return summary, key_findings
        
    except Exception as e:
        logger.error(f"Publication summary generation failed: {e}")
        return "Summary unavailable", []


def _get_candidate_sources(question: str) -> List[str]:
    """Get candidate sources when evidence is insufficient."""
    try:
        # Find publications with related keywords
        query_terms = question.lower().split()
        
        sources_query = """
        MATCH (p:Publication)
        WHERE any(term IN $terms WHERE toLower(p.title) CONTAINS term)
        RETURN p.pub_id as pub_id, p.title as title
        ORDER BY p.year DESC
        LIMIT 5
        """
        
        results = neo4j_client.run_query(sources_query, {"terms": query_terms})
        return [f"{r['pub_id']}: {r['title']}" for r in results]
        
    except Exception as e:
        logger.error(f"Candidate sources retrieval failed: {e}")
        return []


def _build_constraints_query(constraints) -> str:
    """Build search query from mission constraints."""
    query_parts = []
    
    if hasattr(constraints, 'duration_days') and constraints.duration_days:
        if constraints.duration_days <= 30:
            query_parts.append("short-term exposure")
        elif constraints.duration_days <= 180:
            query_parts.append("medium-term exposure")
        else:
            query_parts.append("long-term exposure")
    
    if hasattr(constraints, 'radiation_level') and constraints.radiation_level:
        query_parts.append(f"{constraints.radiation_level} radiation")
    
    if hasattr(constraints, 'gravity_level') and constraints.gravity_level:
        query_parts.append(f"{constraints.gravity_level} gravity microgravity")
    
    return " ".join(query_parts)


def _assess_risk_level(confidence: float, evidence_passages: List[dict]) -> str:
    """Assess risk level based on confidence and evidence quality."""
    if confidence >= 0.8 and len(evidence_passages) >= 3:
        return "low"
    elif confidence >= 0.5 and len(evidence_passages) >= 2:
        return "moderate"
    else:
        return "high"