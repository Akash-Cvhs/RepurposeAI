# GitHub Copilot Instructions for VHS Drug Repurposing Platform

## Project Overview
This is a multi-agent AI system for drug repurposing analysis that integrates clinical trials data, patent information, regulatory guidelines, and market intelligence to generate comprehensive reports.

## Technology Stack
- **Backend:** FastAPI + LangGraph + LangChain
- **Frontend:** Streamlit
- **AI Models:** OpenAI GPT-4 / Anthropic Claude
- **Data Processing:** Pandas, ReportLab
- **Testing:** pytest, unittest.mock

## Project Structure
```
vhs-drug-repurposing/
├── backend/
│   ├── agents/          # Specialized AI agents
│   ├── graph/           # LangGraph workflow
│   ├── data/            # Mock datasets
│   ├── utils/           # Utility functions
│   └── archives/        # Generated reports
├── frontend/            # Streamlit interface
├── docs/                # Architecture & patterns
├── tests/               # Unit & integration tests
└── .github/             # CI/CD configuration
```

## Agent Architecture
Each agent follows this pattern:
- **Input:** State dictionary with query/molecule
- **Processing:** LLM-powered analysis of domain-specific data
- **Output:** Updated state with analysis results

### Agent Types
1. **Master Agent** - Workflow orchestration
2. **Clinical Trials Agent** - Efficacy/safety analysis
3. **Patent Agent** - Freedom-to-operate assessment
4. **Internal Insights Agent** - Regulatory guidance
5. **Web Intelligence Agent** - Market analysis
6. **Drug Analyzer Agent** - Drug properties, mechanisms, and interactions
7. **Report Generator Agent** - Comprehensive reporting

## Development Guidelines

### Code Patterns
- Always use async/await for agent methods
- Follow state management pattern: `Dict[str, Any]`
- Include proper error handling and logging
- Use type hints for all functions
- Follow the agent template in `docs/PATTERNS.md`

### State Schema
```python
{
    "query": str,                    # User research query
    "molecule": str,                 # Optional target molecule
    "run_id": str,                   # Unique execution ID
    "status": str,                   # Workflow status
    "clinical_trials_data": list,    # Trial records
    "patents_data": list,            # Patent records
    "regulatory_insights": str,      # Analysis results
    "drug_properties": dict,         # Drug characteristics
    "mechanism_of_action": str,      # MOA analysis
    "pharmacokinetics": str,         # PK profile
    "drug_interactions": list,       # DDI analysis
    "drug_analysis": str,            # Comprehensive drug analysis
    "report": str                    # Final markdown report
}
```

### Testing Standards
- Use pytest for all tests
- Mock external dependencies (APIs, file I/O)
- Test both success and error scenarios
- Maintain >80% test coverage
- Follow test patterns in `tests/` directory

### Documentation Requirements
- Update `docs/ARCHITECTURE.md` for system changes
- Follow patterns in `docs/PATTERNS.md`
- Update `docs/TASKS.md` for new features
- Include docstrings for all public methods

## Key Rules
1. **Always refer to documentation first** - Check `docs/` before making changes
2. **Follow established patterns** - Use existing agent/workflow patterns
3. **Maintain state consistency** - Preserve state structure across agents
4. **Error handling** - Include try/catch blocks for external calls
5. **Async operations** - Use async/await for all agent methods
6. **Type safety** - Include type hints and validation

## Common Tasks

### Adding New Agent
1. Create agent class in `backend/agents/`
2. Follow template in `docs/PATTERNS.md`
3. Add to workflow in `backend/graph/workflow.py`
4. Create tests in `tests/test_agents.py`
5. Update documentation

### Adding New Data Source
1. Define schema in `docs/DATA_SOURCES.md`
2. Create mock data in `backend/data/`
3. Add processing logic to relevant agent
4. Update filtering and validation functions
5. Add integration tests

### Modifying Workflow
1. Update `backend/graph/workflow.py`
2. Ensure state compatibility
3. Update tests in `tests/test_workflow.py`
4. Document changes in `docs/ARCHITECTURE.md`

## File Naming Conventions
- Agents: `{domain}_agent.py` (e.g., `clinical_trials_agent.py`)
- Tests: `test_{module}.py` (e.g., `test_agents.py`)
- Utils: `{purpose}_utils.py` (e.g., `pdf_utils.py`)
- Data: `{source}.{format}` (e.g., `trials.csv`)

## Environment Setup
```bash
# Backend
cd backend
pip install -r requirements.txt
uvicorn app:app --reload

# Frontend  
cd frontend
pip install -r requirements.txt
streamlit run streamlit_app.py

# Tests
pytest tests/ -v
```

## Important Notes
- This is a demonstration platform with mock data
- Real API integrations are planned for production
- Focus on maintainable, testable code
- Prioritize user experience and performance
- Follow security best practices for API keys