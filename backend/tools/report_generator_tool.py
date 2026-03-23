"""
Report Generator MCP Tool

Generates comprehensive drug repurposing reports from tool results.
"""

from typing import Dict, Any
from utils.llm_utils import get_llm
import json


async def generate_report(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    MCP Tool: Generate comprehensive report from analysis results
    
    Args:
        payload: {
            "query": str (required) - Original user query
            "molecule": str (optional) - Drug/molecule name
            "indication": str (optional) - Disease/indication
            "tool_results": Dict (required) - Results from other tools
            "format": str (optional) - "markdown" or "json" (default: markdown)
        }
    
    Returns:
        {
            "report": str - Generated report
            "format": str - Report format
            "sections": List[str] - Report sections included
        }
    """
    query = payload.get("query", "")
    molecule = payload.get("molecule", "Unknown")
    indication = payload.get("indication", "Unknown")
    tool_results = payload.get("tool_results", {})
    report_format = payload.get("format", "markdown")
    
    if not query:
        return {"error": "Query is required"}
    
    if not tool_results:
        return {"error": "tool_results is required"}
    
    llm = get_llm()
    
    # Build results summary
    summary_lines = []
    for tool_name, result in tool_results.items():
        if isinstance(result, dict):
            data = result.get("data", {})
            if tool_name == "search_clinical_trials":
                count = data.get("count", 0)
                summary_lines.append(f"- Clinical Trials: {count} found")
            elif tool_name == "search_patents":
                count = data.get("count", 0)
                fto = data.get("fto_risk", "unknown")
                summary_lines.append(f"- Patents: {count} found, FTO risk: {fto}")
            elif tool_name == "analyze_drug":
                if data.get("analysis_complete"):
                    summary_lines.append(f"- Drug Analysis: Complete molecular profile")
                else:
                    summary_lines.append(f"- Drug Analysis: Completed")
            elif tool_name == "internal_rag":
                count = len(data.get("results", []))
                summary_lines.append(f"- Internal Documents: {count} relevant")
            elif tool_name == "gather_web_intelligence":
                summary_lines.append(f"- Market Intelligence: Generated")
    
    prompt = f"""
Generate a comprehensive drug repurposing analysis report.

Query: {query}
Molecule: {molecule}
Indication: {indication}

Tools Executed:
{chr(10).join(summary_lines)}

Full Results:
{json.dumps(tool_results, indent=2, default=str)[:5000]}

Generate a structured report with these sections:
1. Executive Summary (2-3 sentences)
2. Clinical Evidence (from clinical trials data)
3. Patent Landscape & FTO Risk (from patent data)
4. Molecular Analysis (from drug analysis data)
5. Market Intelligence (from web intelligence data)
6. Internal Insights (from RAG data)
7. Key Findings (bullet points)
8. Recommendations (3-5 actionable items)
9. Risk Factors (potential concerns)

Format: {"JSON" if report_format == "json" else "Markdown"}
Be specific and cite actual data from the results.
"""
    
    response = await llm.ainvoke(prompt)
    report_content = response.content
    
    sections = [
        "Executive Summary",
        "Clinical Evidence",
        "Patent Landscape",
        "Molecular Analysis",
        "Market Intelligence",
        "Internal Insights",
        "Key Findings",
        "Recommendations",
        "Risk Factors"
    ]
    
    return {
        "report": report_content,
        "format": report_format,
        "sections": sections,
        "query": query,
        "molecule": molecule,
        "indication": indication
    }
