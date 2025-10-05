# Enhanced Router for External Service Integrations
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from ..services.neo4j_client import neo4j_client

# Optional integrations - only import if dependencies are available
try:
    from ..services.meteomatics_service import MeteomaticsService
    METEOMATICS_AVAILABLE = True
except ImportError:
    METEOMATICS_AVAILABLE = False

try:
    from ..services.azure_ai_service import AzureAIService
    AZURE_AVAILABLE = True  
except ImportError:
    AZURE_AVAILABLE = False

try:
    from ..services.miro_service import MiroCollaborationService
    MIRO_AVAILABLE = True
except ImportError:
    MIRO_AVAILABLE = False

logger = logging.getLogger(__name__)

router = APIRouter()

# Pydantic models for request/response
class ResearchEnvironmentRequest(BaseModel):
    publication_id: str
    include_correlations: bool = True

class ResearchEnvironmentResponse(BaseModel):
    publication: Dict[str, Any]
    environmental_context: Dict[str, Any]
    correlations: Dict[str, Any]
    insights: List[str]

class ImageAnalysisRequest(BaseModel):
    image_url: str
    analysis_type: str = "research"  # research, chart, document

class ImageAnalysisResponse(BaseModel):
    research_insights: Dict[str, Any]
    text_content: Optional[Dict[str, Any]]
    processing_status: str

class MiroWorkspaceRequest(BaseModel):
    research_id: str
    title: str
    research_area: str
    collaborators: List[str] = []
    include_templates: bool = True

class MiroWorkspaceResponse(BaseModel):
    workspace_url: str
    board_id: str
    status: str
    collaboration_features: Dict[str, Any]

class TextAnalysisRequest(BaseModel):
    text: str
    analysis_types: List[str] = ["entities", "sentiment", "key_phrases"]

class TextAnalysisResponse(BaseModel):
    entities: List[Dict[str, Any]]
    sentiment: Optional[Dict[str, Any]]
    key_phrases: Optional[List[str]]
    research_indicators: Dict[str, Any]

# Meteomatics Weather/Environmental Integration
@router.get("/environment/space-weather", response_model=Dict[str, Any])
async def get_space_weather_data(
    start_date: str = Query(..., description="Start date in ISO format"),
    end_date: str = Query(..., description="End date in ISO format"),
    meteomatics: MeteomaticsService = Depends()
):
    """Get space weather data for a specific date range"""
    try:
        weather_data = await meteomatics.get_space_weather_context(start_date)
        return {
            "status": "success",
            "data": weather_data,
            "date_range": f"{start_date} to {end_date}"
        }
    except Exception as e:
        logger.error(f"Space weather data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/environment/research-correlation", response_model=ResearchEnvironmentResponse)
async def analyze_research_environment_correlation(
    request: ResearchEnvironmentRequest,
    meteomatics: MeteomaticsService = Depends()
):
    """Analyze correlation between research and environmental conditions"""
    try:
        correlation_data = await meteomatics.analyze_research_environment_correlation(
            request.publication_id
        )
        
        if "error" in correlation_data:
            raise HTTPException(status_code=400, detail=correlation_data["error"])
        
        return ResearchEnvironmentResponse(**correlation_data)
        
    except Exception as e:
        logger.error(f"Research environment correlation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Azure AI Services Integration
@router.post("/ai/analyze-text", response_model=TextAnalysisResponse)
async def enhanced_text_analysis(
    request: TextAnalysisRequest,
    azure_ai: AzureAIService = Depends()
):
    """Enhanced text analysis using Azure AI + SciSpacy"""
    try:
        results = {}
        
        # Entity recognition
        if "entities" in request.analysis_types:
            entity_result = await azure_ai.enhanced_biomedical_ner(request.text)
            results["entities"] = entity_result.get("entities", [])
        
        # Sentiment analysis
        if "sentiment" in request.analysis_types or "key_phrases" in request.analysis_types:
            sentiment_result = await azure_ai.sentiment_analysis_research_text(request.text)
            if "sentiment" in request.analysis_types:
                results["sentiment"] = sentiment_result.get("sentiment")
            if "key_phrases" in request.analysis_types:
                results["key_phrases"] = sentiment_result.get("key_phrases")
            results["research_indicators"] = sentiment_result.get("research_indicators", {})
        
        return TextAnalysisResponse(**results)
        
    except Exception as e:
        logger.error(f"Text analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/ai/analyze-image", response_model=ImageAnalysisResponse)
async def analyze_research_image(
    request: ImageAnalysisRequest,
    azure_ai: AzureAIService = Depends()
):
    """Analyze research images using Azure Computer Vision"""
    try:
        analysis_result = await azure_ai.analyze_research_document_images(request.image_url)
        
        if "error" in analysis_result:
            raise HTTPException(status_code=400, detail=analysis_result["error"])
        
        return ImageAnalysisResponse(
            research_insights=analysis_result["research_insights"],
            text_content=analysis_result.get("text_content"),
            processing_status=analysis_result["processing_status"]
        )
        
    except Exception as e:
        logger.error(f"Image analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Miro Collaboration Integration
@router.post("/collaboration/create-workspace", response_model=MiroWorkspaceResponse)
async def create_miro_research_workspace(
    request: MiroWorkspaceRequest,
    miro: MiroCollaborationService = Depends()
):
    """Create a collaborative research workspace in Miro"""
    try:
        # Get research data from Neo4j
        research_query = """
        MATCH (r:Research {research_id: $research_id})
        OPTIONAL MATCH (r)-[:HAS_PUBLICATION]->(p:Publication)
        OPTIONAL MATCH (r)-[:HAS_ENTITY]->(e:Entity)
        OPTIONAL MATCH (r)-[:HAS_FINDING]->(f:Finding)
        
        RETURN r,
               collect(DISTINCT p{.pub_id, .title, .authors}) as publications,
               collect(DISTINCT e{.entity_id, .name, .entity_type}) as entities,
               collect(DISTINCT f{.finding_id, .description, .confidence}) as findings
        """
        
        result = neo4j_client.run_query(research_query, {"research_id": request.research_id})
        
        if not result:
            raise HTTPException(status_code=404, detail="Research not found")
        
        research_data = result[0]
        
        # Prepare data for Miro workspace
        workspace_data = {
            "title": request.title,
            "research_area": request.research_area,
            "research_id": request.research_id,
            "publications": research_data.get("publications", []),
            "entities": research_data.get("entities", []),
            "key_findings": research_data.get("findings", []),
            "collaborators": request.collaborators,
            "knowledge_graph": {
                "node_count": len(research_data.get("entities", [])),
                "relationship_count": len(research_data.get("findings", [])),
                "density": 0.8,  # Calculate actual density
                "cluster_count": 3  # Calculate actual clusters
            }
        }
        
        # Create Miro workspace
        workspace_result = await miro.create_research_workspace(workspace_data)
        
        if "error" in workspace_result:
            raise HTTPException(status_code=400, detail=workspace_result["error"])
        
        return MiroWorkspaceResponse(
            workspace_url=workspace_result["workspace_url"],
            board_id=workspace_result["board"]["id"],
            status=workspace_result["status"],
            collaboration_features={
                "real_time_editing": True,
                "comment_system": True,
                "template_library": request.include_templates,
                "integration_active": True
            }
        )
        
    except Exception as e:
        logger.error(f"Miro workspace creation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/collaboration/sync-updates/{board_id}")
async def sync_research_updates_to_miro(
    board_id: str,
    research_id: str = Query(...),
    miro: MiroCollaborationService = Depends()
):
    """Sync BioNexus research updates to existing Miro board"""
    try:
        await miro.sync_research_updates(board_id, research_id)
        
        return {
            "status": "success",
            "message": "Research updates synchronized to Miro board",
            "board_id": board_id,
            "research_id": research_id,
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        logger.error(f"Miro sync error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/collaboration/analytics/{board_id}")
async def get_miro_board_analytics(
    board_id: str,
    miro: MiroCollaborationService = Depends()
):
    """Get analytics and usage statistics for a Miro research board"""
    try:
        analytics = await miro.get_board_analytics(board_id)
        
        if "error" in analytics:
            raise HTTPException(status_code=400, detail=analytics["error"])
        
        return analytics
        
    except Exception as e:
        logger.error(f"Miro analytics error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Cross-platform Research Insights
@router.get("/insights/multi-platform/{research_id}")
async def get_multi_platform_research_insights(
    research_id: str,
    include_environment: bool = Query(True),
    include_ai_analysis: bool = Query(True),
    include_collaboration: bool = Query(False),
    meteomatics: MeteomaticsService = Depends(),
    azure_ai: AzureAIService = Depends(),
    miro: MiroCollaborationService = Depends()
):
    """Get comprehensive research insights from multiple platforms"""
    try:
        insights = {
            "research_id": research_id,
            "platforms": {},
            "cross_platform_correlations": {},
            "recommendations": []
        }
        
        # Get base research data
        research_query = """
        MATCH (r:Research {research_id: $research_id})
        OPTIONAL MATCH (r)-[:HAS_PUBLICATION]->(p:Publication)
        RETURN r, collect(p) as publications
        """
        
        base_data = neo4j_client.run_query(research_query, {"research_id": research_id})
        
        if not base_data:
            raise HTTPException(status_code=404, detail="Research not found")
        
        research_info = base_data[0]
        publications = research_info.get("publications", [])
        
        # Environmental analysis
        if include_environment and publications:
            try:
                pub_id = publications[0].get("pub_id")
                if pub_id:
                    env_data = await meteomatics.analyze_research_environment_correlation(pub_id)
                    insights["platforms"]["meteomatics"] = env_data
            except Exception as e:
                logger.warning(f"Environmental analysis failed: {e}")
        
        # AI-powered text analysis
        if include_ai_analysis and publications:
            try:
                # Analyze publication abstracts/titles
                combined_text = " ".join([
                    pub.get("title", "") + " " + pub.get("abstract", "")
                    for pub in publications[:5]  # Limit to first 5 publications
                ])
                
                if combined_text.strip():
                    ai_analysis = await azure_ai.enhanced_biomedical_ner(combined_text)
                    insights["platforms"]["azure_ai"] = ai_analysis
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
        
        # Generate cross-platform insights
        insights["cross_platform_correlations"] = _generate_cross_platform_correlations(
            insights["platforms"]
        )
        
        # Generate recommendations
        insights["recommendations"] = _generate_research_recommendations(
            insights["platforms"], insights["cross_platform_correlations"]
        )
        
        return insights
        
    except Exception as e:
        logger.error(f"Multi-platform insights error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def _generate_cross_platform_correlations(platforms_data: Dict) -> Dict:
    """Generate correlations between different platform insights"""
    correlations = {
        "environmental_ai_correlation": 0.0,
        "confidence_alignment": 0.0,
        "theme_consistency": 0.0
    }
    
    # Analyze correlations between platforms
    meteomatics_data = platforms_data.get("meteomatics", {})
    azure_data = platforms_data.get("azure_ai", {})
    
    if meteomatics_data and azure_data:
        # Check if environmental factors align with AI-detected research themes
        env_correlations = meteomatics_data.get("correlations", {})
        ai_entities = azure_data.get("entities", [])
        
        # Look for space/environmental themes in AI-detected entities
        space_related_entities = [
            e for e in ai_entities 
            if any(keyword in e.get("text", "").lower() 
                  for keyword in ["space", "radiation", "microgravity", "cosmic", "solar"])
        ]
        
        if space_related_entities and env_correlations.get("confidence_score", 0) > 0.3:
            correlations["environmental_ai_correlation"] = min(1.0, 
                len(space_related_entities) * env_correlations["confidence_score"])
    
    return correlations

def _generate_research_recommendations(platforms_data: Dict, correlations: Dict) -> List[str]:
    """Generate actionable research recommendations based on multi-platform analysis"""
    recommendations = []
    
    # Environmental recommendations
    if "meteomatics" in platforms_data:
        env_data = platforms_data["meteomatics"]
        if env_data.get("correlations", {}).get("confidence_score", 0) > 0.5:
            recommendations.append(
                "Consider environmental factors in research design - "
                "strong correlation detected with space weather conditions"
            )
    
    # AI analysis recommendations
    if "azure_ai" in platforms_data:
        ai_data = platforms_data["azure_ai"]
        entity_count = ai_data.get("entity_count", 0)
        
        if entity_count > 20:
            recommendations.append(
                "Rich biomedical entity content detected - "
                "consider developing specialized ontology for this research domain"
            )
        
        confidence_scores = ai_data.get("confidence_scores", {})
        if confidence_scores.get("low_confidence_count", 0) > confidence_scores.get("high_confidence_count", 0):
            recommendations.append(
                "Multiple low-confidence entities detected - "
                "manual review and validation recommended"
            )
    
    # Cross-platform recommendations
    if correlations.get("environmental_ai_correlation", 0) > 0.7:
        recommendations.append(
            "Strong cross-platform correlation detected - "
            "investigate space environment effects on biological systems"
        )
    
    if not recommendations:
        recommendations.append("Continue monitoring research developments across all platforms")
    
    return recommendations