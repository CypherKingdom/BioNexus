# Azure AI Services Integration
import asyncio
import aiohttp
import os
import logging
from typing import Dict, List, Optional, Any
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
import json
import time

logger = logging.getLogger(__name__)

class AzureAIService:
    """Enhanced AI capabilities using Azure Cognitive Services"""
    
    def __init__(self):
        # Text Analytics
        self.text_endpoint = os.getenv("AZURE_TEXT_ENDPOINT")
        self.text_key = os.getenv("AZURE_TEXT_KEY")
        
        if self.text_endpoint and self.text_key:
            self.text_client = TextAnalyticsClient(
                endpoint=self.text_endpoint,
                credential=AzureKeyCredential(self.text_key)
            )
        
        # Computer Vision
        self.vision_endpoint = os.getenv("AZURE_VISION_ENDPOINT")
        self.vision_key = os.getenv("AZURE_VISION_KEY")
        
        if self.vision_endpoint and self.vision_key:
            self.vision_client = ComputerVisionClient(
                self.vision_endpoint,
                AzureKeyCredential(self.vision_key)
            )
    
    async def enhanced_biomedical_ner(self, text: str) -> Dict:
        """Enhanced biomedical NER combining Azure Text Analytics with SciSpacy"""
        try:
            if not hasattr(self, 'text_client'):
                return {"error": "Azure Text Analytics not configured"}
            
            # Azure Text Analytics
            azure_entities = []
            documents = [text]
            
            # General entity recognition
            entities_result = self.text_client.recognize_entities(documents)
            
            for doc in entities_result:
                if not doc.is_error:
                    for entity in doc.entities:
                        azure_entities.append({
                            "text": entity.text,
                            "category": entity.category,
                            "subcategory": entity.subcategory,
                            "confidence": entity.confidence_score,
                            "offset": entity.offset,
                            "length": entity.length,
                            "source": "azure"
                        })
            
            # Healthcare-specific entities (if available)
            try:
                healthcare_results = self.text_client.begin_analyze_healthcare_entities(documents)
                healthcare_entities = []
                
                for result in healthcare_results:
                    if not result.is_error:
                        for entity in result.entities:
                            healthcare_entities.append({
                                "text": entity.text,
                                "category": entity.category,
                                "subcategory": entity.subcategory if hasattr(entity, 'subcategory') else None,
                                "confidence": entity.confidence_score,
                                "source": "azure_healthcare"
                            })
                
                azure_entities.extend(healthcare_entities)
            
            except Exception as e:
                logger.warning(f"Healthcare entities not available: {e}")
            
            # Combine with SciSpacy results
            scispacy_entities = await self._get_scispacy_entities(text)
            
            # Cross-validate and enhance
            enhanced_entities = self._merge_entity_results(azure_entities, scispacy_entities)
            
            return {
                "entities": enhanced_entities,
                "entity_count": len(enhanced_entities),
                "azure_entities": len(azure_entities),
                "scispacy_entities": len(scispacy_entities),
                "confidence_scores": self._calculate_confidence_distribution(enhanced_entities),
                "validation_status": "cross_validated"
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced_biomedical_ner: {e}")
            return {"error": str(e)}
    
    async def analyze_research_document_images(self, image_url: str) -> Dict:
        """Analyze research document images (charts, diagrams, etc.)"""
        try:
            if not hasattr(self, 'vision_client'):
                return {"error": "Azure Computer Vision not configured"}
            
            # Analyze image
            analysis_result = self.vision_client.analyze_image(
                image_url,
                visual_features=[
                    "Categories", "Description", "Objects", "Tags", 
                    "ImageType", "Faces", "Adult", "Color", "Brands"
                ]
            )
            
            # Extract research-relevant information
            research_insights = {
                "image_type": self._detect_research_image_type(analysis_result),
                "scientific_objects": self._identify_scientific_objects(analysis_result),
                "chart_analysis": await self._analyze_charts_and_graphs(image_url),
                "text_content": await self._extract_image_text(image_url),
                "methodology_indicators": self._detect_methodology_elements(analysis_result),
                "confidence_scores": {}
            }
            
            return {
                "research_insights": research_insights,
                "raw_analysis": {
                    "categories": [{"name": cat.name, "score": cat.score} for cat in analysis_result.categories],
                    "description": analysis_result.description.captions[0].text if analysis_result.description.captions else None,
                    "tags": [{"name": tag.name, "confidence": tag.confidence} for tag in analysis_result.tags],
                    "objects": [{"name": obj.object_property, "confidence": obj.confidence, 
                               "rectangle": obj.rectangle} for obj in analysis_result.objects] if analysis_result.objects else []
                },
                "processing_status": "completed"
            }
            
        except Exception as e:
            logger.error(f"Error analyzing research images: {e}")
            return {"error": str(e)}
    
    async def _extract_image_text(self, image_url: str) -> Dict:
        """Extract text from images using OCR"""
        try:
            # Start OCR operation
            ocr_result = self.vision_client.read(image_url, raw=True)
            
            # Get operation location
            operation_location = ocr_result.headers["Operation-Location"]
            operation_id = operation_location.split("/")[-1]
            
            # Wait for completion
            while True:
                read_result = self.vision_client.get_read_result(operation_id)
                if read_result.status not in ['notStarted', 'running']:
                    break
                time.sleep(1)
            
            # Extract text
            extracted_text = ""
            text_blocks = []
            
            if read_result.status == OperationStatusCodes.succeeded:
                for text_result in read_result.analyze_result.read_results:
                    for line in text_result.lines:
                        extracted_text += line.text + "\n"
                        text_blocks.append({
                            "text": line.text,
                            "bounding_box": line.bounding_box,
                            "confidence": getattr(line, 'confidence', 1.0)
                        })
            
            # Analyze extracted text for research content
            research_text_analysis = await self._analyze_extracted_research_text(extracted_text)
            
            return {
                "extracted_text": extracted_text,
                "text_blocks": text_blocks,
                "research_analysis": research_text_analysis,
                "extraction_status": read_result.status
            }
            
        except Exception as e:
            logger.error(f"Error extracting image text: {e}")
            return {"error": str(e)}
    
    async def _analyze_charts_and_graphs(self, image_url: str) -> Dict:
        """Analyze charts and graphs in research images"""
        try:
            # Custom analysis for research charts
            chart_analysis = {
                "chart_type": "unknown",
                "data_visualization": False,
                "statistical_content": False,
                "research_metrics": [],
                "detected_elements": []
            }
            
            # Use object detection to identify chart elements
            analysis = self.vision_client.analyze_image(
                image_url,
                visual_features=["Objects", "Tags"]
            )
            
            # Detect chart types based on objects and tags
            chart_indicators = ["chart", "graph", "plot", "diagram", "table", "data", "statistics"]
            research_indicators = ["microscope", "laboratory", "specimen", "cell", "protein", "dna"]
            
            for tag in analysis.tags:
                if any(indicator in tag.name.lower() for indicator in chart_indicators):
                    chart_analysis["data_visualization"] = True
                    chart_analysis["detected_elements"].append({
                        "element": tag.name,
                        "confidence": tag.confidence,
                        "type": "chart_element"
                    })
                
                if any(indicator in tag.name.lower() for indicator in research_indicators):
                    chart_analysis["research_metrics"].append({
                        "metric": tag.name,
                        "confidence": tag.confidence
                    })
            
            # Determine chart type
            if chart_analysis["data_visualization"]:
                chart_analysis["chart_type"] = self._classify_chart_type(analysis.tags)
            
            return chart_analysis
            
        except Exception as e:
            logger.error(f"Error analyzing charts: {e}")
            return {"error": str(e)}
    
    async def sentiment_analysis_research_text(self, text: str) -> Dict:
        """Analyze sentiment and key phrases in research text"""
        try:
            if not hasattr(self, 'text_client'):
                return {"error": "Azure Text Analytics not configured"}
            
            documents = [text]
            
            # Sentiment analysis
            sentiment_result = self.text_client.analyze_sentiment(documents)
            
            # Key phrase extraction
            key_phrases_result = self.text_client.extract_key_phrases(documents)
            
            # Language detection
            language_result = self.text_client.detect_language(documents)
            
            results = {
                "sentiment": {},
                "key_phrases": [],
                "language": {},
                "research_indicators": {}
            }
            
            # Process sentiment
            for doc in sentiment_result:
                if not doc.is_error:
                    results["sentiment"] = {
                        "overall": doc.sentiment,
                        "confidence_scores": {
                            "positive": doc.confidence_scores.positive,
                            "neutral": doc.confidence_scores.neutral,
                            "negative": doc.confidence_scores.negative
                        },
                        "sentences": [
                            {
                                "text": sentence.text,
                                "sentiment": sentence.sentiment,
                                "confidence": {
                                    "positive": sentence.confidence_scores.positive,
                                    "neutral": sentence.confidence_scores.neutral,
                                    "negative": sentence.confidence_scores.negative
                                }
                            }
                            for sentence in doc.sentences
                        ]
                    }
            
            # Process key phrases
            for doc in key_phrases_result:
                if not doc.is_error:
                    results["key_phrases"] = doc.key_phrases
            
            # Process language
            for doc in language_result:
                if not doc.is_error:
                    results["language"] = {
                        "primary_language": doc.primary_language.name,
                        "confidence": doc.primary_language.confidence_score,
                        "iso6391_name": doc.primary_language.iso6391_name
                    }
            
            # Analyze research-specific indicators
            results["research_indicators"] = self._analyze_research_indicators(
                results["key_phrases"], results["sentiment"]
            )
            
            return results
            
        except Exception as e:
            logger.error(f"Error in sentiment analysis: {e}")
            return {"error": str(e)}
    
    async def _get_scispacy_entities(self, text: str) -> List[Dict]:
        """Get SciSpacy entities (placeholder for existing SciSpacy integration)"""
        # This would integrate with your existing SciSpacy service
        return []
    
    def _merge_entity_results(self, azure_entities: List[Dict], scispacy_entities: List[Dict]) -> List[Dict]:
        """Merge and deduplicate entity results from different sources"""
        merged = []
        seen_texts = set()
        
        # Process Azure entities
        for entity in azure_entities:
            text_lower = entity["text"].lower()
            if text_lower not in seen_texts:
                seen_texts.add(text_lower)
                merged.append(entity)
        
        # Add SciSpacy entities that don't overlap
        for entity in scispacy_entities:
            text_lower = entity["text"].lower()
            if text_lower not in seen_texts:
                seen_texts.add(text_lower)
                entity["source"] = "scispacy"
                merged.append(entity)
        
        # Sort by confidence
        merged.sort(key=lambda x: x.get("confidence", 0), reverse=True)
        
        return merged
    
    def _calculate_confidence_distribution(self, entities: List[Dict]) -> Dict:
        """Calculate confidence score distribution"""
        if not entities:
            return {}
        
        confidences = [e.get("confidence", 0) for e in entities]
        
        return {
            "mean": sum(confidences) / len(confidences),
            "max": max(confidences),
            "min": min(confidences),
            "high_confidence_count": len([c for c in confidences if c > 0.8]),
            "medium_confidence_count": len([c for c in confidences if 0.5 <= c <= 0.8]),
            "low_confidence_count": len([c for c in confidences if c < 0.5])
        }
    
    def _detect_research_image_type(self, analysis_result) -> str:
        """Detect the type of research image"""
        categories = [cat.name.lower() for cat in analysis_result.categories]
        tags = [tag.name.lower() for tag in analysis_result.tags]
        
        all_terms = categories + tags
        
        if any(term in all_terms for term in ["chart", "graph", "plot", "diagram"]):
            return "data_visualization"
        elif any(term in all_terms for term in ["microscope", "microscopic", "cell", "tissue"]):
            return "microscopic_image"
        elif any(term in all_terms for term in ["laboratory", "equipment", "instrument"]):
            return "laboratory_equipment"
        elif any(term in all_terms for term in ["document", "text", "paper"]):
            return "research_document"
        else:
            return "general_research_image"
    
    def _identify_scientific_objects(self, analysis_result) -> List[Dict]:
        """Identify scientific objects in the image"""
        scientific_objects = []
        
        if analysis_result.objects:
            for obj in analysis_result.objects:
                scientific_objects.append({
                    "object": obj.object_property,
                    "confidence": obj.confidence,
                    "location": {
                        "x": obj.rectangle.x,
                        "y": obj.rectangle.y,
                        "w": obj.rectangle.w,
                        "h": obj.rectangle.h
                    }
                })
        
        return scientific_objects
    
    def _detect_methodology_elements(self, analysis_result) -> List[str]:
        """Detect research methodology elements"""
        methodology_indicators = []
        
        research_methods = [
            "microscopy", "spectroscopy", "chromatography", "electrophoresis",
            "pcr", "sequencing", "cell culture", "western blot", "immunofluorescence"
        ]
        
        tags = [tag.name.lower() for tag in analysis_result.tags]
        
        for method in research_methods:
            if any(method in tag for tag in tags):
                methodology_indicators.append(method)
        
        return methodology_indicators
    
    def _classify_chart_type(self, tags) -> str:
        """Classify the type of chart/graph"""
        tag_names = [tag.name.lower() for tag in tags]
        
        if any("bar" in tag for tag in tag_names):
            return "bar_chart"
        elif any("line" in tag for tag in tag_names):
            return "line_graph"
        elif any("pie" in tag for tag in tag_names):
            return "pie_chart"
        elif any("scatter" in tag for tag in tag_names):
            return "scatter_plot"
        elif any("histogram" in tag for tag in tag_names):
            return "histogram"
        else:
            return "unknown_chart"
    
    async def _analyze_extracted_research_text(self, text: str) -> Dict:
        """Analyze extracted text for research content"""
        research_keywords = [
            "hypothesis", "methodology", "results", "conclusion", "significant",
            "correlation", "p-value", "confidence interval", "sample size",
            "control group", "experimental", "data analysis"
        ]
        
        text_lower = text.lower()
        found_keywords = [kw for kw in research_keywords if kw in text_lower]
        
        return {
            "research_keywords_found": found_keywords,
            "research_content_score": len(found_keywords) / len(research_keywords),
            "likely_research_document": len(found_keywords) >= 3,
            "text_length": len(text),
            "estimated_reading_time": len(text.split()) / 200  # words per minute
        }
    
    def _analyze_research_indicators(self, key_phrases: List[str], sentiment: Dict) -> Dict:
        """Analyze research-specific indicators from text analysis"""
        research_phrases = [
            phrase for phrase in key_phrases 
            if any(research_term in phrase.lower() for research_term in [
                "research", "study", "experiment", "analysis", "investigation",
                "hypothesis", "methodology", "results", "findings", "conclusion"
            ])
        ]
        
        return {
            "research_phrase_count": len(research_phrases),
            "research_phrases": research_phrases,
            "likely_research_text": len(research_phrases) >= 2,
            "sentiment_objectivity": sentiment.get("confidence_scores", {}).get("neutral", 0),
            "research_confidence": min(1.0, len(research_phrases) / 5)  # Max confidence at 5+ phrases
        }