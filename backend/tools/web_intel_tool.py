"""
Web Intelligence MCP Tool

Gathers market intelligence and competitive landscape data.
Can be invoked independently via MCP protocol.
"""

from typing import Dict, Any
from utils.llm_utils import get_llm


async def gather_web_intelligence(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Gather web intelligence and market insights
    
    Args:
        payload: {
            "query": str (required) - Search query
            "molecule": str (optional) - Drug/molecule name
            "indication": str (optional) - Disease/indication
            "focus": str (optional) - "market", "competitive", "regulatory", "all"
        }
    
    Returns:
        {
            "intelligence": str - Market intelligence analysis
            "focus_areas": List[str] - Areas covered
            "sources": List[str] - Data sources used
            "confidence": float - Confidence score (0-1)
            "error": str (optional) - Error message if failed
        }
    """
    query = payload.get("query", "")
    molecule = payload.get("molecule", "")
    indication = payload.get("indication", "")
    focus = payload.get("focus", "all")
    
    if not query and not molecule:
        return {
            "intelligence": "",
            "focus_areas": [],
            "sources": [],
            "confidence": 0.0,
            "error": "Query or molecule name is required"
        }
    
    try:
        llm = get_llm()
        
        # Build focused prompt based on request
        focus_areas = []
        if focus in ["market", "all"]:
            focus_areas.append("Market size and opportunity")
            focus_areas.append("Commercial viability")
        if focus in ["competitive", "all"]:
            focus_areas.append("Competitive landscape")
            focus_areas.append("Key players and partnerships")
        if focus in ["regulatory", "all"]:
            focus_areas.append("Regulatory pathway")
            focus_areas.append("Market access considerations")
        
        prompt = f"""
Generate market intelligence analysis for drug repurposing opportunity:

Query: {query}
Molecule: {molecule or "Not specified"}
Indication: {indication or "Not specified"}

Provide analysis covering:
{chr(10).join(f"- {area}" for area in focus_areas)}

Note: This is a mock analysis for demonstration purposes.
In production, this would integrate real-time web data sources like:
- News APIs (Google News, Bing News)
- Market research databases
- Regulatory databases (FDA, EMA)
- Scientific publications (PubMed)
- Company press releases

Provide structured market intelligence in 3-4 paragraphs.
"""
        
        response = await llm.ainvoke(prompt)
        intelligence = response.content
        
        return {
            "intelligence": intelligence,
            "focus_areas": focus_areas,
            "sources": ["mock_data"],  # In production: actual sources
            "confidence": 0.6,  # Mock data has lower confidence
            "molecule": molecule,
            "indication": indication,
            "query": query
        }
        
    except Exception as exc:
        return {
            "intelligence": "",
            "focus_areas": [],
            "sources": [],
            "confidence": 0.0,
            "error": str(exc)
        }
