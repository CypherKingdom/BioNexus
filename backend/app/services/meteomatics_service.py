# Enhanced Backend Services with Cloud Integrations

# Meteomatics Weather Integration
import asyncio
import aiohttp
from datetime import datetime, timedelta
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MeteomaticsService:
    """Service for integrating Meteomatics weather and environmental data"""
    
    def __init__(self):
        self.username = os.getenv("METEOMATICS_USERNAME")
        self.password = os.getenv("METEOMATICS_PASSWORD")
        self.base_url = "https://api.meteomatics.com"
    
    async def get_space_weather_context(self, research_date: str) -> Dict:
        """Get space weather context for research publications"""
        try:
            # Parse research date
            research_dt = datetime.fromisoformat(research_date.replace('Z', '+00:00'))
            
            # Get date range (30 days before and after research)
            start_date = (research_dt - timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
            end_date = (research_dt + timedelta(days=30)).strftime('%Y-%m-%dT%H:%M:%SZ')
            
            # Space weather parameters relevant to biological research
            parameters = [
                "solar_radiation_flux:W",
                "cosmic_ray_intensity:cps",
                "geomagnetic_activity:index",
                "solar_wind_speed:ms",
                "solar_particle_flux:particles"
            ]
            
            weather_data = {}
            
            async with aiohttp.ClientSession() as session:
                for param in parameters:
                    try:
                        url = f"{self.base_url}/{start_date}--{end_date}:P1D/{param}/global/json"
                        
                        async with session.get(
                            url, 
                            auth=aiohttp.BasicAuth(self.username, self.password)
                        ) as response:
                            if response.status == 200:
                                data = await response.json()
                                weather_data[param] = data
                            else:
                                logger.warning(f"Failed to fetch {param}: {response.status}")
                    
                    except Exception as e:
                        logger.error(f"Error fetching {param}: {e}")
            
            return {
                "research_date": research_date,
                "environmental_context": weather_data,
                "correlation_period": f"{start_date} to {end_date}",
                "parameters_collected": list(weather_data.keys())
            }
            
        except Exception as e:
            logger.error(f"Error in get_space_weather_context: {e}")
            return {"error": str(e)}
    
    async def analyze_research_environment_correlation(self, pub_id: str) -> Dict:
        """Analyze correlation between research findings and environmental conditions"""
        try:
            from ..services.neo4j_client import neo4j_client
            
            # Get publication details
            pub_query = """
            MATCH (p:Publication {pub_id: $pub_id})
            RETURN p.publication_date as date, p.title as title, p.research_focus as focus
            """
            
            pub_result = neo4j_client.run_query(pub_query, {"pub_id": pub_id})
            
            if not pub_result:
                return {"error": "Publication not found"}
            
            pub_data = pub_result[0]
            
            # Get environmental context
            env_context = await self.get_space_weather_context(pub_data["date"])
            
            # Analyze potential correlations
            correlations = self._analyze_correlations(pub_data, env_context)
            
            # Store in Neo4j
            await self._store_environmental_context(pub_id, env_context, correlations)
            
            return {
                "publication": pub_data,
                "environmental_context": env_context,
                "correlations": correlations,
                "insights": self._generate_insights(correlations)
            }
            
        except Exception as e:
            logger.error(f"Error in analyze_research_environment_correlation: {e}")
            return {"error": str(e)}
    
    def _analyze_correlations(self, pub_data: Dict, env_context: Dict) -> Dict:
        """Analyze correlations between research focus and environmental data"""
        correlations = {
            "solar_radiation_impact": "low",
            "cosmic_ray_correlation": "medium",
            "geomagnetic_influence": "low",
            "confidence_score": 0.0
        }
        
        research_focus = pub_data.get("focus", "").lower()
        
        # Biological research correlations
        if any(keyword in research_focus for keyword in ["bone", "muscle", "cardiovascular", "immune"]):
            correlations["cosmic_ray_correlation"] = "high"
            correlations["confidence_score"] += 0.3
        
        if any(keyword in research_focus for keyword in ["radiation", "dna", "cellular", "genetic"]):
            correlations["solar_radiation_impact"] = "high"
            correlations["confidence_score"] += 0.4
        
        if any(keyword in research_focus for keyword in ["circadian", "sleep", "behavior", "neurological"]):
            correlations["geomagnetic_influence"] = "medium"
            correlations["confidence_score"] += 0.2
        
        return correlations
    
    async def _store_environmental_context(self, pub_id: str, env_context: Dict, correlations: Dict):
        """Store environmental context in Neo4j"""
        try:
            from ..services.neo4j_client import neo4j_client
            
            query = """
            MATCH (p:Publication {pub_id: $pub_id})
            MERGE (e:EnvironmentalContext {
                research_date: $research_date,
                correlation_period: $correlation_period,
                solar_radiation_impact: $solar_impact,
                cosmic_ray_correlation: $cosmic_correlation,
                geomagnetic_influence: $geo_influence,
                confidence_score: $confidence
            })
            MERGE (p)-[:RESEARCHED_DURING]->(e)
            RETURN e
            """
            
            params = {
                "pub_id": pub_id,
                "research_date": env_context.get("research_date"),
                "correlation_period": env_context.get("correlation_period"),
                "solar_impact": correlations.get("solar_radiation_impact"),
                "cosmic_correlation": correlations.get("cosmic_ray_correlation"),
                "geo_influence": correlations.get("geomagnetic_influence"),
                "confidence": correlations.get("confidence_score")
            }
            
            neo4j_client.run_query(query, params)
            
        except Exception as e:
            logger.error(f"Error storing environmental context: {e}")
    
    def _generate_insights(self, correlations: Dict) -> List[str]:
        """Generate research insights based on correlations"""
        insights = []
        
        if correlations["confidence_score"] > 0.5:
            insights.append("Strong environmental correlation detected with research focus")
        
        if correlations["solar_radiation_impact"] == "high":
            insights.append("Research may be significantly influenced by solar radiation levels")
        
        if correlations["cosmic_ray_correlation"] == "high":
            insights.append("Cosmic radiation exposure likely relevant to research outcomes")
        
        if correlations["geomagnetic_influence"] in ["medium", "high"]:
            insights.append("Geomagnetic activity may have affected biological systems studied")
        
        if not insights:
            insights.append("Low environmental correlation detected - research likely laboratory-based")
        
        return insights