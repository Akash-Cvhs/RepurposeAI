from typing import Dict, Any
from langgraph.graph import StateGraph, END
from agents.master_agent import MasterAgent
from agents.clinical_trials_agent import ClinicalTrialsAgent
from agents.patent_agent import PatentAgent
from agents.internal_insights_agent import InternalInsightsAgent
from agents.web_intel_agent import WebIntelAgent
from agents.drug_analyzer_agent import DrugAnalyzerAgent
from agents.report_generator_agent import ReportGeneratorAgent

# Initialize agents
master_agent = MasterAgent()
clinical_agent = ClinicalTrialsAgent()
patent_agent = PatentAgent()
insights_agent = InternalInsightsAgent()
web_agent = WebIntelAgent()
drug_agent = DrugAnalyzerAgent()
report_agent = ReportGeneratorAgent()

def create_workflow():
    """Create the LangGraph workflow for drug repurposing analysis"""
    
    # Define the state schema
    workflow = StateGraph(dict)
    
    # Add nodes
    workflow.add_node("plan", master_agent.plan_analysis)
    workflow.add_node("clinical_trials", clinical_agent.analyze_trials)
    workflow.add_node("patents", patent_agent.analyze_patents)
    workflow.add_node("insights", insights_agent.analyze_guidelines)
    workflow.add_node("web_intel", web_agent.gather_intelligence)
    workflow.add_node("drug_analysis", drug_agent.analyze_drug)
    workflow.add_node("coordinate", master_agent.coordinate_agents)
    workflow.add_node("report", report_agent.generate_report)
    
    # Define the flow
    workflow.set_entry_point("plan")
    
    # Parallel execution of analysis agents
    workflow.add_edge("plan", "clinical_trials")
    workflow.add_edge("plan", "patents")
    workflow.add_edge("plan", "insights")
    workflow.add_edge("plan", "web_intel")
    workflow.add_edge("plan", "drug_analysis")
    
    # Coordination after parallel execution
    workflow.add_edge("clinical_trials", "coordinate")
    workflow.add_edge("patents", "coordinate")
    workflow.add_edge("insights", "coordinate")
    workflow.add_edge("web_intel", "coordinate")
    workflow.add_edge("drug_analysis", "coordinate")
    
    # Report generation
    workflow.add_edge("coordinate", "report")
    workflow.add_edge("report", END)
    
    return workflow.compile()

async def run_drug_repurposing_workflow(query: str, molecule: str = None, run_id: str = None) -> Dict[str, Any]:
    """Execute the complete drug repurposing analysis workflow"""
    
    # Initialize state
    initial_state = {
        "query": query,
        "molecule": molecule,
        "run_id": run_id,
        "status": "initialized"
    }
    
    # Create and run workflow
    workflow = create_workflow()
    result = await workflow.ainvoke(initial_state)
    
    return result