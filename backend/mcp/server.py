"""
Optional MCP (Model Context Protocol) server for VHS Drug Repurposing Platform
This provides structured tools for external AI systems to interact with the platform
"""

from typing import List, Dict, Any
import json
import pandas as pd
from pathlib import Path

# MCP Server Implementation (Optional Extension)
class VHSMCPServer:
    """MCP server for drug repurposing platform tools"""
    
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.archives_dir = self.base_dir / "archives"
    
    async def list_trials(self, condition: str = None, molecule: str = None) -> List[Dict[str, Any]]:
        """List clinical trials with optional filtering"""
        try:
            trials_df = pd.read_csv(self.data_dir / "trials.csv")
            
            if condition:
                trials_df = trials_df[trials_df['condition'].str.contains(condition, case=False, na=False)]
            
            if molecule:
                trials_df = trials_df[trials_df['intervention'].str.contains(molecule, case=False, na=False)]
            
            return trials_df.to_dict('records')
        
        except FileNotFoundError:
            return []
    
    async def list_patents(self, query: str = None, active_only: bool = True) -> List[Dict[str, Any]]:
        """List patents with optional filtering"""
        try:
            patents_df = pd.read_csv(self.data_dir / "patents.csv")
            
            if active_only:
                patents_df = patents_df[patents_df['status'] == 'Active']
            
            if query:
                mask = (patents_df['title'].str.contains(query, case=False, na=False) |
                       patents_df['abstract'].str.contains(query, case=False, na=False))
                patents_df = patents_df[mask]
            
            return patents_df.to_dict('records')
        
        except FileNotFoundError:
            return []
    
    async def list_reports(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List generated reports"""
        try:
            runs_file = self.archives_dir / "runs.json"
            
            if runs_file.exists():
                with open(runs_file, 'r') as f:
                    runs = json.load(f)
                
                return runs[-limit:] if runs else []
            
            return []
        
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    async def get_guidelines(self, therapeutic_area: str = None) -> Dict[str, Any]:
        """Get regulatory guidelines"""
        try:
            guidelines_file = self.data_dir / "guidelines.json"
            
            with open(guidelines_file, 'r') as f:
                guidelines = json.load(f)
            
            if therapeutic_area and therapeutic_area in guidelines.get('therapeutic_areas', {}):
                return {
                    'therapeutic_area': therapeutic_area,
                    'guidelines': guidelines['therapeutic_areas'][therapeutic_area]
                }
            
            return guidelines
        
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

# MCP Tool Definitions
MCP_TOOLS = [
    {
        "name": "list_trials",
        "description": "List clinical trials with optional filtering by condition or molecule",
        "parameters": {
            "type": "object",
            "properties": {
                "condition": {
                    "type": "string",
                    "description": "Filter by medical condition"
                },
                "molecule": {
                    "type": "string", 
                    "description": "Filter by drug/molecule name"
                }
            }
        }
    },
    {
        "name": "list_patents",
        "description": "List patents with optional filtering",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query for patent title or abstract"
                },
                "active_only": {
                    "type": "boolean",
                    "description": "Only return active patents",
                    "default": True
                }
            }
        }
    },
    {
        "name": "list_reports", 
        "description": "List previously generated analysis reports",
        "parameters": {
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of reports to return",
                    "default": 10
                }
            }
        }
    },
    {
        "name": "get_guidelines",
        "description": "Get regulatory guidelines, optionally filtered by therapeutic area",
        "parameters": {
            "type": "object", 
            "properties": {
                "therapeutic_area": {
                    "type": "string",
                    "description": "Specific therapeutic area (oncology, neurology, cardiology)"
                }
            }
        }
    }
]

if __name__ == "__main__":
    # Example usage
    server = VHSMCPServer()
    
    # This would be integrated with an actual MCP server framework
    print("VHS Drug Repurposing MCP Server initialized")
    print(f"Available tools: {[tool['name'] for tool in MCP_TOOLS]}")