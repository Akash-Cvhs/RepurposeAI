# VHS Drug Repurposing Platform - Architecture

## System Overview

The VHS Drug Repurposing Platform is a multi-agent AI system designed to analyze drug repurposing opportunities by integrating clinical trials data, patent information, regulatory guidelines, and market intelligence.

## Architecture Components

### 1. Multi-Agent System
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Master Agent  │───▶│  Clinical Trials │───▶│  Report         │
│   (Orchestrator)│    │  Agent           │    │  Generator      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       ▲
         ▼                       ▼                       │
┌─────────────────┐    ┌──────────────────┐             │
│   Patent Agent  │    │  Internal        │─────────────┘
│   (FTO Analysis)│    │  Insights Agent  │             │
└─────────────────┘    └──────────────────┘             │
         │                       │                       │
         ▼                       ▼                       │
┌─────────────────┐    ┌──────────────────┐             │
│  Web Intel      │    │  Drug Analyzer   │─────────────┘
│  Agent          │    │  Agent           │
└─────────────────┘    └──────────────────┘
         │                       │
         ▼                       ▼
         └──────────────┬────────┘
                        ▼
              ┌──────────────────┐
              │  Coordination    │
              │  & State Mgmt    │
              └──────────────────┘
```

### 2. Agent Responsibilities

#### Master Agent
- **Role:** Workflow orchestration and planning
- **Functions:** 
  - Analysis planning based on query/molecule
  - Agent coordination and state management
  - Error handling and recovery

#### Clinical Trials Agent
- **Role:** Clinical evidence analysis
- **Functions:**
  - Search and filter relevant trials
  - Efficacy and safety signal extraction
  - Patient population analysis

#### Patent Agent
- **Role:** Intellectual property landscape analysis
- **Functions:**
  - Patent search and filtering
  - Freedom-to-operate (FTO) risk assessment
  - Expiration date analysis

#### Internal Insights Agent
- **Role:** Regulatory and strategic guidance
- **Functions:**
  - Regulatory pathway recommendations
  - Guidelines interpretation
  - Strategic risk assessment

#### Web Intelligence Agent
- **Role:** Market and competitive intelligence
- **Functions:**
  - Market landscape analysis
  - Competitive positioning
  - Commercial viability assessment

#### Drug Analyzer Agent
- **Role:** Comprehensive drug property and mechanism analysis
- **Functions:**
  - Drug properties and characteristics analysis
  - Mechanism of action evaluation
  - Pharmacokinetic profile assessment
  - Drug-drug interaction analysis
  - Repurposing potential scoring

#### Report Generator Agent
- **Role:** Comprehensive report compilation
- **Functions:**
  - Executive summary generation
  - Multi-source data integration
  - PDF report creation

### 3. Data Flow & State Management

#### State Schema
```python
{
    "query": str,                    # User research query
    "molecule": str,                 # Optional target molecule
    "run_id": str,                   # Unique execution identifier
    "status": str,                   # Workflow status
    "analysis_plan": dict,           # Agent execution plan
    "clinical_trials_data": list,    # Trial records
    "clinical_trials_analysis": str, # Clinical insights
    "patents_data": list,            # Patent records
    "patent_analysis": str,          # FTO assessment
    "guidelines_data": dict,         # Regulatory guidelines
    "regulatory_insights": str,      # Regulatory analysis
    "web_intelligence": str,         # Market intelligence
    "drug_properties": dict,         # Drug characteristics
    "mechanism_of_action": str,      # MOA analysis
    "pharmacokinetics": str,         # PK profile
    "drug_interactions": list,       # DDI analysis
    "repurposing_potential": str,    # Repurposing assessment
    "drug_analysis": str,            # Comprehensive drug analysis
    "executive_summary": str,        # Key findings summary
    "report": str,                   # Full markdown report
    "completed_agents": list         # Execution tracking
}
```

#### Workflow Execution
1. **Initialization:** Master agent creates analysis plan
2. **Parallel Execution:** Specialized agents run concurrently
3. **Coordination:** Master agent aggregates results
4. **Report Generation:** Comprehensive report compilation
5. **Storage:** PDF generation and archive management

### 4. Technology Stack

#### Backend (FastAPI)
- **Framework:** FastAPI for REST API
- **Orchestration:** LangGraph for workflow management
- **AI Integration:** LangChain for LLM interactions
- **Data Processing:** Pandas for data manipulation
- **Report Generation:** ReportLab for PDF creation

#### Frontend (Streamlit)
- **Interface:** Chat-based query input
- **Visualization:** Analysis history and results
- **File Management:** PDF download and archive access

#### Data Storage
- **Structured Data:** CSV files for trials/patents
- **Configuration:** JSON for guidelines/settings
- **Reports:** PDF files with metadata indexing
- **State:** JSON-based run history tracking

### 5. Integration Points

#### External APIs (Future)
- ClinicalTrials.gov API
- Patent databases (USPTO, EPO)
- PubMed/literature databases
- Market intelligence services

#### Internal Data Sources
- Mock clinical trials dataset
- Mock patent database
- Regulatory guidelines repository
- Historical analysis archive

### 6. Scalability Considerations

#### Horizontal Scaling
- Stateless agent design
- Async/await patterns
- Database connection pooling
- Caching strategies

#### Performance Optimization
- Parallel agent execution
- Efficient data filtering
- Incremental processing
- Result caching

### 7. Security & Compliance

#### Data Protection
- API key management
- Secure file storage
- Access control mechanisms
- Audit trail maintenance

#### Regulatory Compliance
- Data retention policies
- Privacy protection measures
- Validation and verification
- Change control processes