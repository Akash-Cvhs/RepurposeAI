import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from backend.graph.workflow import run_drug_repurposing_workflow, create_workflow

class TestWorkflow:
    
    @pytest.mark.asyncio
    async def test_workflow_creation(self):
        """Test workflow graph creation"""
        
        workflow = create_workflow()
        
        # Verify workflow is created successfully
        assert workflow is not None
    
    @pytest.mark.asyncio
    async def test_run_drug_repurposing_workflow_basic(self):
        """Test basic workflow execution"""
        
        # Mock all agent methods
        with patch('backend.agents.master_agent.MasterAgent.plan_analysis') as mock_plan:
            with patch('backend.agents.clinical_trials_agent.ClinicalTrialsAgent.analyze_trials') as mock_trials:
                with patch('backend.agents.patent_agent.PatentAgent.analyze_patents') as mock_patents:
                    with patch('backend.agents.internal_insights_agent.InternalInsightsAgent.analyze_guidelines') as mock_insights:
                        with patch('backend.agents.web_intel_agent.WebIntelAgent.gather_intelligence') as mock_web:
                            with patch('backend.agents.master_agent.MasterAgent.coordinate_agents') as mock_coord:
                                with patch('backend.agents.report_generator_agent.ReportGeneratorAgent.generate_report') as mock_report:
                                    
                                    # Configure mock returns
                                    mock_plan.return_value = {"status": "planned", "analysis_plan": {}}
                                    mock_trials.return_value = {"clinical_trials_analysis": "test"}
                                    mock_patents.return_value = {"patent_analysis": "test"}
                                    mock_insights.return_value = {"regulatory_insights": "test"}
                                    mock_web.return_value = {"web_intelligence": "test"}
                                    mock_coord.return_value = {"status": "coordinated"}
                                    mock_report.return_value = {"status": "completed", "report": "test report"}
                                    
                                    # Execute workflow
                                    result = await run_drug_repurposing_workflow(
                                        query="test query",
                                        molecule="test molecule",
                                        run_id="test_run"
                                    )
                                    
                                    # Verify execution
                                    assert result is not None
                                    assert "query" in result
                                    assert result["query"] == "test query"
    
    @pytest.mark.asyncio
    async def test_workflow_state_management(self):
        """Test workflow state management"""
        
        initial_state = {
            "query": "Alzheimer's treatment",
            "molecule": "aspirin",
            "run_id": "state_test_123"
        }
        
        # Mock workflow execution to return state
        with patch('backend.graph.workflow.create_workflow') as mock_create:
            mock_workflow = AsyncMock()
            mock_workflow.ainvoke.return_value = {
                **initial_state,
                "status": "completed",
                "report": "Generated report"
            }
            mock_create.return_value = mock_workflow
            
            result = await run_drug_repurposing_workflow(**initial_state)
            
            # Verify state preservation and updates
            assert result["query"] == initial_state["query"]
            assert result["molecule"] == initial_state["molecule"]
            assert result["run_id"] == initial_state["run_id"]
            assert result["status"] == "completed"
            assert "report" in result
    
    @pytest.mark.asyncio
    async def test_workflow_error_handling(self):
        """Test workflow error handling"""
        
        with patch('backend.graph.workflow.create_workflow') as mock_create:
            mock_workflow = AsyncMock()
            mock_workflow.ainvoke.side_effect = Exception("Workflow execution failed")
            mock_create.return_value = mock_workflow
            
            with pytest.raises(Exception) as exc_info:
                await run_drug_repurposing_workflow(
                    query="test query",
                    molecule="test molecule"
                )
            
            assert "Workflow execution failed" in str(exc_info.value)

class TestWorkflowIntegration:
    
    @pytest.mark.asyncio
    async def test_end_to_end_minimal(self):
        """Test minimal end-to-end workflow execution"""
        
        # This test uses real workflow but mocks external dependencies
        with patch('pandas.read_csv') as mock_csv:
            with patch('builtins.open', create=True) as mock_open:
                with patch('json.load') as mock_json:
                    
                    # Mock data sources
                    mock_csv.return_value = MagicMock()
                    mock_csv.return_value.empty = True
                    mock_csv.return_value.to_dict.return_value = []
                    
                    mock_json.return_value = {}
                    
                    # Mock LLM responses
                    with patch('langchain_openai.ChatOpenAI') as mock_llm:
                        mock_response = MagicMock()
                        mock_response.content = "Mock analysis result"
                        mock_llm.return_value.ainvoke.return_value = mock_response
                        
                        result = await run_drug_repurposing_workflow(
                            query="test integration",
                            molecule="test compound",
                            run_id="integration_test"
                        )
                        
                        # Verify basic workflow completion
                        assert result is not None
                        assert "query" in result
                        assert "status" in result