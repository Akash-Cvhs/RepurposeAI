# Development Patterns & Standards

## Agent Structure Pattern

### Standard Agent Template
```python
from typing import Dict, Any
from langchain_openai import ChatOpenAI
from config import DEFAULT_LLM_MODEL

class ExampleAgent:
    """Agent description and purpose"""
    
    def __init__(self):
        self.llm = ChatOpenAI(model=DEFAULT_LLM_MODEL)
    
    async def main_function(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Primary agent function with state management"""
        
        # Extract inputs from state
        query = state.get("query", "")
        molecule = state.get("molecule", "")
        
        # Perform agent-specific processing
        result = await self._process_data(query, molecule)
        
        # Update state with results
        state["agent_output"] = result
        
        return state
    
    async def _process_data(self, query: str, molecule: str) -> str:
        """Private method for core processing logic"""
        
        prompt = f"""
        Agent-specific prompt template:
        Query: {query}
        Molecule: {molecule}
        
        Instructions for LLM processing...
        """
        
        response = await self.llm.ainvoke(prompt)
        return response.content
```

### Key Patterns

#### 1. State Management
- Always accept and return `Dict[str, Any]` state
- Extract inputs using `.get()` with defaults
- Update state with new results before returning
- Maintain immutable state principles

#### 2. Error Handling
```python
async def robust_function(self, state: Dict[str, Any]) -> Dict[str, Any]:
    try:
        # Main processing logic
        result = await self._process_data(state)
        state["success"] = True
        state["result"] = result
        
    except FileNotFoundError:
        state["success"] = False
        state["error"] = "Data file not found"
        state["result"] = "No data available"
        
    except Exception as e:
        state["success"] = False
        state["error"] = str(e)
        state["result"] = "Processing failed"
    
    return state
```

#### 3. Data Filtering
```python
def _filter_data(self, df: pd.DataFrame, query: str, molecule: str) -> pd.DataFrame:
    """Standard data filtering pattern"""
    
    if df.empty:
        return df
    
    # Initialize mask
    mask = pd.Series([True] * len(df))
    
    # Apply filters conditionally
    if molecule:
        mask &= df['relevant_column'].str.contains(molecule, case=False, na=False)
    
    if query:
        mask &= (df['column1'].str.contains(query, case=False, na=False) |
                df['column2'].str.contains(query, case=False, na=False))
    
    return df[mask].head(10)  # Limit results
```

## Logging & Monitoring

### Logging Standards
```python
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class AgentWithLogging:
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        run_id = state.get("run_id", "unknown")
        
        self.logger.info(f"Starting processing for run {run_id}")
        
        try:
            result = await self._do_work(state)
            self.logger.info(f"Completed processing for run {run_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"Error in run {run_id}: {str(e)}")
            raise
```

### Performance Monitoring
```python
import time
from functools import wraps

def monitor_performance(func):
    """Decorator for performance monitoring"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            
            logging.info(f"{func.__name__} completed in {duration:.2f}s")
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            logging.error(f"{func.__name__} failed after {duration:.2f}s: {str(e)}")
            raise
    
    return wrapper
```

## Configuration Management

### Environment Variables
```python
# config.py pattern
import os
from pathlib import Path

# Required configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable required")

# Optional configurations with defaults
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "10"))

# Path configurations
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
```

### Validation Patterns
```python
from pydantic import BaseModel, validator

class QueryRequest(BaseModel):
    query: str
    molecule: Optional[str] = None
    
    @validator('query')
    def query_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Query cannot be empty')
        return v.strip()
    
    @validator('molecule')
    def molecule_format(cls, v):
        if v and len(v.strip()) < 2:
            raise ValueError('Molecule name too short')
        return v.strip() if v else None
```

## Testing Patterns

### Unit Test Structure
```python
import pytest
from unittest.mock import AsyncMock, patch
from agents.example_agent import ExampleAgent

class TestExampleAgent:
    
    @pytest.fixture
    def agent(self):
        return ExampleAgent()
    
    @pytest.fixture
    def sample_state(self):
        return {
            "query": "test query",
            "molecule": "test molecule",
            "run_id": "test_run_123"
        }
    
    @pytest.mark.asyncio
    async def test_main_function_success(self, agent, sample_state):
        """Test successful agent execution"""
        
        with patch.object(agent, '_process_data', return_value="test result"):
            result = await agent.main_function(sample_state)
            
            assert result["agent_output"] == "test result"
            assert "query" in result
    
    @pytest.mark.asyncio
    async def test_main_function_error_handling(self, agent, sample_state):
        """Test agent error handling"""
        
        with patch.object(agent, '_process_data', side_effect=Exception("Test error")):
            with pytest.raises(Exception):
                await agent.main_function(sample_state)
```

### Integration Test Pattern
```python
@pytest.mark.asyncio
async def test_workflow_integration():
    """Test complete workflow execution"""
    
    initial_state = {
        "query": "Alzheimer's treatment",
        "molecule": "aspirin",
        "run_id": "integration_test"
    }
    
    # Mock external dependencies
    with patch('agents.clinical_trials_agent.pd.read_csv') as mock_csv:
        mock_csv.return_value = create_mock_dataframe()
        
        result = await run_drug_repurposing_workflow(**initial_state)
        
        assert result["status"] == "completed"
        assert "report" in result
```

## Code Quality Standards

### Type Hints
- Use type hints for all function parameters and returns
- Import types from `typing` module
- Use `Optional[T]` for nullable parameters
- Use `Dict[str, Any]` for state objects

### Documentation
- Include docstrings for all classes and public methods
- Use Google-style docstring format
- Document complex algorithms and business logic
- Maintain up-to-date README files

### Code Organization
- Keep functions under 50 lines when possible
- Use descriptive variable and function names
- Group related functionality in modules
- Follow PEP 8 style guidelines