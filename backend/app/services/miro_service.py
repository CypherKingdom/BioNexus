# Miro Collaboration Integration Service
import asyncio
import aiohttp
import json
import os
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime

logger = logging.getLogger(__name__)

class MiroCollaborationService:
    """Service for integrating Miro collaborative whiteboards with BioNexus research"""
    
    def __init__(self):
        self.api_key = os.getenv("MIRO_API_KEY")
        self.base_url = "https://api.miro.com/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    async def create_research_workspace(self, research_data: Dict) -> Dict:
        """Create a collaborative research workspace in Miro"""
        try:
            if not self.api_key:
                return {"error": "Miro API key not configured"}
            
            # Create team board
            board_data = {
                "name": f"BioNexus Research: {research_data.get('title', 'Unknown Research')}",
                "description": f"Collaborative space for {research_data.get('research_area', 'biomedical')} research analysis",
                "policy": {
                    "permissionsPolicy": {
                        "collaborationToolsStartAccess": "all_editors",
                        "copyAccess": "team_members_with_editing_rights",
                        "sharingAccess": "team_members_with_editing_rights"
                    },
                    "sharingPolicy": {
                        "access": "private",
                        "inviteToAccountAndBoardLinkAccess": "no_access"
                    }
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/boards",
                    headers=self.headers,
                    json=board_data
                ) as response:
                    if response.status == 201:
                        board = await response.json()
                        
                        # Populate with research content
                        await self.populate_research_content(board["id"], research_data)
                        
                        # Add collaboration templates
                        await self.add_collaboration_templates(board["id"])
                        
                        return {
                            "board": board,
                            "workspace_url": board.get("viewLink"),
                            "edit_url": board.get("sharingPolicy", {}).get("access") == "private" 
                                       and board.get("viewLink") or None,
                            "status": "created"
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to create Miro board: {response.status} - {error_text}")
                        return {"error": f"Failed to create board: {response.status}"}
                        
        except Exception as e:
            logger.error(f"Error creating research workspace: {e}")
            return {"error": str(e)}
    
    async def populate_research_content(self, board_id: str, research_data: Dict):
        """Populate Miro board with BioNexus research content"""
        try:
            widgets = []
            
            # Research Overview Section
            widgets.append({
                "type": "sticker",
                "text": f"🧬 Research Overview\n\nTitle: {research_data.get('title', 'N/A')}\n"
                       f"Area: {research_data.get('research_area', 'N/A')}\n"
                       f"Publications: {len(research_data.get('publications', []))}\n"
                       f"Entities: {len(research_data.get('entities', []))}\n"
                       f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                "style": {
                    "stickerColor": "blue",
                    "textAlign": "left"
                },
                "x": 100,
                "y": 100,
                "width": 300
            })
            
            # Knowledge Graph Summary
            if research_data.get('knowledge_graph'):
                kg_data = research_data['knowledge_graph']
                widgets.append({
                    "type": "shape",
                    "text": f"📊 Knowledge Graph\n\n"
                           f"Nodes: {kg_data.get('node_count', 0)}\n"
                           f"Relationships: {kg_data.get('relationship_count', 0)}\n"
                           f"Density: {kg_data.get('density', 0):.2f}\n"
                           f"Clusters: {kg_data.get('cluster_count', 0)}",
                    "style": {
                        "shapeType": "rectangle",
                        "backgroundColor": "#E6F3FF",
                        "borderColor": "#0077B6",
                        "fontSize": "14",
                        "textAlign": "left"
                    },
                    "x": 450,
                    "y": 100,
                    "width": 250,
                    "height": 180
                })
            
            # Key Findings Section
            key_findings = research_data.get('key_findings', [])[:6]  # Limit to 6 findings
            for i, finding in enumerate(key_findings):
                row = i // 3
                col = i % 3
                
                widgets.append({
                    "type": "sticker",
                    "text": f"🔍 Finding {i+1}\n\n{finding.get('description', 'N/A')}\n\n"
                           f"Confidence: {finding.get('confidence', 0):.1%}\n"
                           f"Publications: {finding.get('publication_count', 0)}",
                    "style": {
                        "stickerColor": "yellow",
                        "textAlign": "left"
                    },
                    "x": 100 + (col * 280),
                    "y": 350 + (row * 200),
                    "width": 260
                })
            
            # Research Timeline
            timeline_data = research_data.get('timeline', [])
            if timeline_data:
                timeline_y = 800
                widgets.append({
                    "type": "text",
                    "text": "📅 Research Timeline",
                    "style": {
                        "fontSize": "24",
                        "fontFamily": "arial",
                        "textAlign": "center",
                        "color": "#333333"
                    },
                    "x": 400,
                    "y": timeline_y - 50,
                    "width": 200
                })
                
                for i, event in enumerate(timeline_data[:10]):  # Limit to 10 events
                    widgets.append({
                        "type": "sticker",
                        "text": f"{event.get('date', 'N/A')}\n{event.get('description', 'N/A')[:50]}...",
                        "style": {
                            "stickerColor": "light_green",
                            "textAlign": "left"
                        },
                        "x": 50 + (i * 150),
                        "y": timeline_y,
                        "width": 140,
                        "height": 100
                    })
            
            # Collaboration Areas
            widgets.append({
                "type": "shape",
                "text": "👥 Team Discussion Area\n\n"
                       "Add your insights, questions, and ideas here.\n"
                       "Use sticky notes to contribute!",
                "style": {
                    "shapeType": "rectangle",
                    "backgroundColor": "#F0FFF0",
                    "borderColor": "#32CD32",
                    "fontSize": "16",
                    "textAlign": "center"
                },
                "x": 100,
                "y": 1000,
                "width": 400,
                "height": 150
            })
            
            widgets.append({
                "type": "shape",
                "text": "🎯 Action Items & Next Steps\n\n"
                       "1. Review key findings\n"
                       "2. Identify research gaps\n"
                       "3. Plan follow-up studies\n"
                       "4. Schedule team meetings",
                "style": {
                    "shapeType": "rectangle",
                    "backgroundColor": "#FFF0F5",
                    "borderColor": "#FF69B4",
                    "fontSize": "14",
                    "textAlign": "left"
                },
                "x": 550,
                "y": 1000,
                "width": 300,
                "height": 150
            })
            
            # Create widgets in batches
            await self.create_widgets_batch(board_id, widgets)
            
        except Exception as e:
            logger.error(f"Error populating research content: {e}")
    
    async def add_collaboration_templates(self, board_id: str):
        """Add collaboration templates and frameworks to the board"""
        try:
            templates = []
            
            # Research Analysis Framework
            framework_x = 1000
            framework_y = 100
            
            templates.extend([
                {
                    "type": "text",
                    "text": "🔬 Research Analysis Framework",
                    "style": {
                        "fontSize": "20",
                        "fontFamily": "arial",
                        "textAlign": "center",
                        "color": "#2E8B57"
                    },
                    "x": framework_x,
                    "y": framework_y - 30,
                    "width": 300
                },
                {
                    "type": "sticker",
                    "text": "📋 Methodology\n\n• Research approach\n• Data collection\n• Analysis methods\n• Validation",
                    "style": {"stickerColor": "light_blue"},
                    "x": framework_x,
                    "y": framework_y + 20,
                    "width": 200
                },
                {
                    "type": "sticker",
                    "text": "📊 Results\n\n• Key metrics\n• Statistical significance\n• Visualizations\n• Interpretations",
                    "style": {"stickerColor": "orange"},
                    "x": framework_x + 220,
                    "y": framework_y + 20,
                    "width": 200
                },
                {
                    "type": "sticker",
                    "text": "🎯 Implications\n\n• Clinical relevance\n• Future research\n• Applications\n• Limitations",
                    "style": {"stickerColor": "pink"},
                    "x": framework_x + 110,
                    "y": framework_y + 170,
                    "width": 200
                }
            ])
            
            # Hypothesis Development Section
            hypo_x = 1000
            hypo_y = 400
            
            templates.append({
                "type": "shape",
                "text": "💡 Hypothesis Development\n\n"
                       "Current Hypothesis:\n"
                       "_________________________________\n\n"
                       "Supporting Evidence:\n"
                       "• \n"
                       "• \n"
                       "• \n\n"
                       "Contradicting Evidence:\n"
                       "• \n"
                       "• \n\n"
                       "Revised Hypothesis:\n"
                       "_________________________________",
                "style": {
                    "shapeType": "rectangle",
                    "backgroundColor": "#FFFACD",
                    "borderColor": "#DAA520",
                    "fontSize": "12",
                    "textAlign": "left"
                },
                "x": hypo_x,
                "y": hypo_y,
                "width": 350,
                "height": 300
            })
            
            # Literature Review Matrix
            lit_x = 1400
            lit_y = 400
            
            templates.append({
                "type": "shape",
                "text": "📚 Literature Review Matrix\n\n"
                       "Study | Method | Sample | Key Finding | Quality\n"
                       "------|--------|--------|-------------|--------\n"
                       "      |        |        |             |\n"
                       "      |        |        |             |\n"
                       "      |        |        |             |\n"
                       "      |        |        |             |\n"
                       "      |        |        |             |",
                "style": {
                    "shapeType": "rectangle",
                    "backgroundColor": "#F0F8FF",
                    "borderColor": "#4169E1",
                    "fontSize": "10",
                    "fontFamily": "courier",
                    "textAlign": "left"
                },
                "x": lit_x,
                "y": lit_y,
                "width": 400,
                "height": 300
            })
            
            await self.create_widgets_batch(board_id, templates)
            
        except Exception as e:
            logger.error(f"Error adding collaboration templates: {e}")
    
    async def create_widgets_batch(self, board_id: str, widgets: List[Dict]):
        """Create widgets in batches to avoid API limits"""
        batch_size = 10  # Miro API typically allows 10-20 widgets per batch
        
        for i in range(0, len(widgets), batch_size):
            batch = widgets[i:i + batch_size]
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        f"{self.base_url}/boards/{board_id}/widgets",
                        headers=self.headers,
                        json={"widgets": batch}
                    ) as response:
                        if response.status not in [200, 201]:
                            error_text = await response.text()
                            logger.warning(f"Batch widget creation failed: {response.status} - {error_text}")
                
                # Small delay between batches to respect rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error creating widget batch: {e}")
    
    async def sync_research_updates(self, board_id: str, research_id: str):
        """Sync BioNexus research updates to Miro board"""
        try:
            # Get latest research data from BioNexus
            from ..services.neo4j_client import neo4j_client
            
            # Fetch updated research data
            query = """
            MATCH (r:Research {research_id: $research_id})
            OPTIONAL MATCH (r)-[:HAS_PUBLICATION]->(p:Publication)
            OPTIONAL MATCH (r)-[:HAS_ENTITY]->(e:Entity)
            OPTIONAL MATCH (r)-[:HAS_FINDING]->(f:Finding)
            
            RETURN r, 
                   count(DISTINCT p) as pub_count,
                   count(DISTINCT e) as entity_count,
                   collect(DISTINCT f) as findings
            """
            
            result = neo4j_client.run_query(query, {"research_id": research_id})
            
            if result:
                research_data = result[0]
                
                # Create update notification widget
                update_widget = {
                    "type": "sticker",
                    "text": f"🔄 Research Update\n\n"
                           f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
                           f"Publications: {research_data['pub_count']}\n"
                           f"Entities: {research_data['entity_count']}\n"
                           f"New Findings: {len(research_data.get('findings', []))}\n\n"
                           f"View details in BioNexus →",
                    "style": {
                        "stickerColor": "red",
                        "textAlign": "left"
                    },
                    "x": 50,
                    "y": 50,
                    "width": 250
                }
                
                await self.create_widgets_batch(board_id, [update_widget])
                
                # Notify collaborators
                await self.notify_collaborators(
                    board_id, 
                    f"Research data updated in BioNexus. New findings: {len(research_data.get('findings', []))}"
                )
            
        except Exception as e:
            logger.error(f"Error syncing research updates: {e}")
    
    async def notify_collaborators(self, board_id: str, message: str):
        """Send notifications to board collaborators"""
        try:
            # Get board collaborators
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/boards/{board_id}/members",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        members = await response.json()
                        
                        # Create notification for each member
                        # Note: This is a simplified version - actual implementation
                        # would use Miro's notification system or external email/Slack
                        
                        logger.info(f"Notifying {len(members)} collaborators: {message}")
                    
        except Exception as e:
            logger.error(f"Error notifying collaborators: {e}")
    
    async def get_board_analytics(self, board_id: str) -> Dict:
        """Get analytics and usage statistics for a research board"""
        try:
            async with aiohttp.ClientSession() as session:
                # Get board info
                async with session.get(
                    f"{self.base_url}/boards/{board_id}",
                    headers=self.headers
                ) as response:
                    if response.status == 200:
                        board_data = await response.json()
                        
                        # Get widgets count
                        async with session.get(
                            f"{self.base_url}/boards/{board_id}/widgets",
                            headers=self.headers
                        ) as widgets_response:
                            widgets_data = []
                            if widgets_response.status == 200:
                                widgets_data = await widgets_response.json()
                        
                        analytics = {
                            "board_info": {
                                "id": board_data.get("id"),
                                "name": board_data.get("name"),
                                "created_at": board_data.get("createdAt"),
                                "modified_at": board_data.get("modifiedAt")
                            },
                            "usage_stats": {
                                "total_widgets": len(widgets_data),
                                "widget_types": self._analyze_widget_types(widgets_data),
                                "collaboration_level": self._assess_collaboration_level(widgets_data),
                                "last_activity": board_data.get("modifiedAt")
                            },
                            "research_progress": {
                                "completion_estimate": self._estimate_completion(widgets_data),
                                "active_discussions": self._count_discussion_items(widgets_data)
                            }
                        }
                        
                        return analytics
                    
                    else:
                        return {"error": f"Failed to get board data: {response.status}"}
            
        except Exception as e:
            logger.error(f"Error getting board analytics: {e}")
            return {"error": str(e)}
    
    def _analyze_widget_types(self, widgets_data: List[Dict]) -> Dict:
        """Analyze distribution of widget types on the board"""
        widget_types = {}
        
        for widget in widgets_data:
            widget_type = widget.get("type", "unknown")
            widget_types[widget_type] = widget_types.get(widget_type, 0) + 1
        
        return widget_types
    
    def _assess_collaboration_level(self, widgets_data: List[Dict]) -> str:
        """Assess the level of collaboration based on widget content"""
        collaboration_indicators = 0
        
        for widget in widgets_data:
            text = widget.get("text", "").lower()
            if any(indicator in text for indicator in [
                "discussion", "question", "idea", "comment", "feedback", "suggestion"
            ]):
                collaboration_indicators += 1
        
        if collaboration_indicators > 10:
            return "high"
        elif collaboration_indicators > 5:
            return "medium"
        else:
            return "low"
    
    def _estimate_completion(self, widgets_data: List[Dict]) -> float:
        """Estimate research progress completion based on board content"""
        total_sections = 0
        completed_sections = 0
        
        for widget in widgets_data:
            text = widget.get("text", "").lower()
            
            # Count research sections
            if any(section in text for section in [
                "methodology", "results", "conclusion", "hypothesis", "analysis"
            ]):
                total_sections += 1
                
                # Check if section appears completed
                if any(completion in text for completion in [
                    "completed", "done", "finished", "confirmed", "validated"
                ]):
                    completed_sections += 1
        
        if total_sections == 0:
            return 0.0
        
        return completed_sections / total_sections
    
    def _count_discussion_items(self, widgets_data: List[Dict]) -> int:
        """Count active discussion items on the board"""
        discussion_count = 0
        
        for widget in widgets_data:
            text = widget.get("text", "").lower()
            if any(discussion_term in text for discussion_term in [
                "?", "discuss", "question", "clarify", "explain", "why", "how"
            ]):
                discussion_count += 1
        
        return discussion_count