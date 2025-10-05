from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import logging

# Import the Azure AI service
from app.services.azure_ai_service import AzureAIService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/azure", tags=["Azure AI"])

# Initialize Azure service
azure_service = AzureAIService()

class TextAnalysisRequest(BaseModel):
    text: str

class ImageAnalysisRequest(BaseModel):
    image_url: str

@router.post("/analyze-biomedical-text")
async def analyze_biomedical_text(request: TextAnalysisRequest):
    """
    Enhanced biomedical Named Entity Recognition using Azure Text Analytics + SciSpacy
    
    Combines Azure's powerful text analytics with specialized biomedical models
    for comprehensive entity extraction from research texts.
    """
    try:
        result = await azure_service.enhanced_biomedical_ner(request.text)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "analysis_type": "enhanced_biomedical_ner",
            "data": result,
            "azure_integration": "active"
        }
        
    except Exception as e:
        logger.error(f"Error in biomedical text analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-sentiment")
async def analyze_research_sentiment(request: TextAnalysisRequest):
    """
    Analyze sentiment and extract key phrases from research text
    
    Provides detailed sentiment analysis optimized for scientific literature,
    including research-specific indicators and confidence scoring.
    """
    try:
        result = await azure_service.sentiment_analysis_research_text(request.text)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "analysis_type": "research_sentiment_analysis",
            "data": result,
            "azure_integration": "active"
        }
        
    except Exception as e:
        logger.error(f"Error in sentiment analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Sentiment analysis failed: {str(e)}")

@router.post("/analyze-image")
async def analyze_research_image(request: ImageAnalysisRequest):
    """
    Analyze research document images (charts, diagrams, microscopy images)
    
    Uses Azure Computer Vision to extract insights from scientific images,
    including chart analysis, OCR for text extraction, and research methodology detection.
    """
    try:
        result = await azure_service.analyze_research_document_images(request.image_url)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return {
            "status": "success",
            "analysis_type": "research_image_analysis",
            "data": result,
            "azure_integration": "active"
        }
        
    except Exception as e:
        logger.error(f"Error in image analysis: {e}")
        raise HTTPException(status_code=500, detail=f"Image analysis failed: {str(e)}")

@router.get("/health")
async def azure_health_check():
    """
    Check Azure AI services connectivity and configuration
    """
    try:
        # Check if Azure services are properly configured
        has_text_analytics = hasattr(azure_service, 'text_client')
        has_computer_vision = hasattr(azure_service, 'vision_client')
        
        return {
            "status": "healthy",
            "services": {
                "text_analytics": "configured" if has_text_analytics else "not_configured",
                "computer_vision": "configured" if has_computer_vision else "not_configured"
            },
            "azure_integration": "active",
            "ready_for_production": has_text_analytics and has_computer_vision
        }
        
    except Exception as e:
        logger.error(f"Azure health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "azure_integration": "error"
        }

@router.get("/capabilities")
async def get_azure_capabilities():
    """
    Get available Azure AI capabilities and feature descriptions
    """
    return {
        "available_features": {
            "enhanced_biomedical_ner": {
                "description": "Advanced biomedical entity recognition combining Azure + SciSpacy",
                "input": "Research text",
                "output": "Entities with confidence scores and source attribution",
                "use_cases": ["Literature review", "Knowledge graph enrichment", "Research analysis"]
            },
            "research_sentiment_analysis": {
                "description": "Sentiment analysis optimized for scientific literature",
                "input": "Research text",
                "output": "Sentiment scores, key phrases, research indicators",
                "use_cases": ["Publication analysis", "Research trend detection", "Content categorization"]
            },
            "research_image_analysis": {
                "description": "Computer vision for scientific images and documents",
                "input": "Image URL",
                "output": "Chart analysis, OCR text, methodology detection",
                "use_cases": ["Document digitization", "Chart data extraction", "Research methodology identification"]
            }
        },
        "integration_status": "ready",
        "supported_domains": [
            "Biomedical research",
            "Life sciences",
            "Clinical studies",
            "Scientific publications",
            "Research methodology"
        ]
    }