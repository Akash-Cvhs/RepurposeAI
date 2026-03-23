import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import pandas as pd
from backend.agents.clinical_trials_agent import ClinicalTrialsAgent
from backend.agents.patent_agent import PatentAgent
from backend.agents.master_agent import MasterAgent
from backend.agents.drug_analyzer_agent import DrugAnalyzerAgent

class TestClinicalTrialsAgent:
    
    @pytest.fixture
    def agent(self):
        return ClinicalTrialsAgent()
    
    @pytest.fixture
    def sample_state(self):
        return {
            "query": "Alzheimer's disease",
            "molecule": "aspirin",
            "run_id": "test_run_123"
        }
    
    @pytest.fixture
    def mock_trials_df(self):
        return pd.DataFrame([
            {
                'nct_id': 'NCT12345678',
                'title': 'Aspirin for Alzheimer\'s Disease',
                'condition': 'Alzheimer\'s Disease',
                'intervention': 'Aspirin 81mg',
                'phase': 'Phase 3',
                'status': 'Recruiting',
                'sponsor': 'University Medical Center',
                'enrollment': 2000
            }
        ])
    
    @pytest.mark.asyncio
    async def test_analyze_trials_success(self, agent, sample_state, mock_trials_df):
        """Test successful clinical trials analysis"""
        
        with patch('pandas.read_csv', return_value=mock_trials_df):
            with patch.object(agent, '_analyze_findings', return_value="Test analysis"):
                result = await agent.analyze_trials(sample_state)
                
                assert "clinical_trials_data" in result
                assert "clinical_trials_analysis" in result
                assert result["clinical_trials_analysis"] == "Test analysis"
                assert len(result["clinical_trials_data"]) == 1
    
    @pytest.mark.asyncio
    async def test_analyze_trials_no_file(self, agent, sample_state):
        """Test handling of missing data file"""
        
        with patch('pandas.read_csv', side_effect=FileNotFoundError):
            result = await agent.analyze_trials(sample_state)
            
            assert result["clinical_trials_data"] == []
            assert result["clinical_trials_analysis"] == "No clinical trials data available"
    
    def test_filter_trials(self, agent, mock_trials_df):
        """Test trial filtering logic"""
        
        # Test molecule filtering
        filtered = agent._filter_trials(mock_trials_df, "", "aspirin")
        assert len(filtered) == 1
        
        # Test query filtering
        filtered = agent._filter_trials(mock_trials_df, "Alzheimer", "")
        assert len(filtered) == 1
        
        # Test no matches
        filtered = agent._filter_trials(mock_trials_df, "cancer", "")
        assert len(filtered) == 0

class TestPatentAgent:
    
    @pytest.fixture
    def agent(self):
        return PatentAgent()
    
    @pytest.fixture
    def sample_state(self):
        return {
            "query": "Alzheimer's treatment",
            "molecule": "aspirin",
            "run_id": "test_run_456"
        }
    
    @pytest.fixture
    def mock_patents_df(self):
        return pd.DataFrame([
            {
                'patent_number': 'US10123456',
                'title': 'Methods for treating Alzheimer\'s with aspirin',
                'assignee': 'Pharma Inc',
                'filing_date': '2015-03-15',
                'expiration_date': '2035-03-15',
                'abstract': 'Novel methods for using aspirin in Alzheimer\'s treatment',
                'status': 'Active'
            }
        ])
    
    @pytest.mark.asyncio
    async def test_analyze_patents_success(self, agent, sample_state, mock_patents_df):
        """Test successful patent analysis"""
        
        with patch('pandas.read_csv', return_value=mock_patents_df):
            with patch.object(agent, '_analyze_fto_risks', return_value="FTO analysis"):
                result = await agent.analyze_patents(sample_state)
                
                assert "patents_data" in result
                assert "patent_analysis" in result
                assert result["patent_analysis"] == "FTO analysis"
                assert len(result["patents_data"]) == 1
    
    def test_filter_patents(self, agent, mock_patents_df):
        """Test patent filtering logic"""
        
        # Test molecule filtering
        filtered = agent._filter_patents(mock_patents_df, "", "aspirin")
        assert len(filtered) == 1
        
        # Test query filtering
        filtered = agent._filter_patents(mock_patents_df, "Alzheimer", "")
        assert len(filtered) == 1

class TestMasterAgent:
    
    @pytest.fixture
    def agent(self):
        return MasterAgent()
    
    @pytest.fixture
    def sample_state(self):
        return {
            "query": "drug repurposing opportunity",
            "molecule": "metformin",
            "run_id": "test_run_789"
        }
    
    @pytest.mark.asyncio
    async def test_plan_analysis(self, agent, sample_state):
        """Test analysis planning"""
        
        result = await agent.plan_analysis(sample_state)
        
        assert "analysis_plan" in result
        assert result["status"] == "planned"
        
        plan = result["analysis_plan"]
        assert plan["clinical_trials"] is True
        assert plan["patents"] is True
        assert plan["internal_insights"] is True
        assert plan["drug_analysis"] is True
        assert plan["report_generation"] is True
    
    @pytest.mark.asyncio
    async def test_coordinate_agents(self, agent, sample_state):
        """Test agent coordination"""
        
        sample_state["analysis_plan"] = {
            "clinical_trials": True,
            "patents": True,
            "internal_insights": True,
            "web_intel": True,
            "drug_analysis": True,
            "report_generation": True
        }
        
        result = await agent.coordinate_agents(sample_state)
        
        assert "completed_agents" in result
        assert result["status"] == "coordinated"
        assert len(result["completed_agents"]) == 5  # Excludes report_generation

class TestDrugAnalyzerAgent:
    
    @pytest.fixture
    def agent(self):
        return DrugAnalyzerAgent()
    
    @pytest.fixture
    def sample_state(self):
        return {
            "query": "Alzheimer's disease treatment",
            "molecule": "aspirin",
            "run_id": "test_run_drug_001"
        }
    
    @pytest.fixture
    def sample_state_no_molecule(self):
        return {
            "query": "cardiovascular disease prevention",
            "run_id": "test_run_drug_002"
        }
    
    @pytest.mark.asyncio
    async def test_analyze_drug_with_molecule(self, agent, sample_state):
        """Test drug analysis with specified molecule"""
        
        # Mock all the internal analysis methods
        with patch.object(agent, '_analyze_drug_properties', return_value={"molecule_name": "aspirin", "analysis": "test"}):
            with patch.object(agent, '_analyze_mechanism_of_action', return_value="COX inhibition"):
                with patch.object(agent, '_analyze_pharmacokinetics', return_value="Rapid absorption"):
                    with patch.object(agent, '_analyze_drug_interactions', return_value=[]):
                        with patch.object(agent, '_assess_repurposing_potential', return_value="High potential"):
                            with patch.object(agent, '_compile_drug_analysis', return_value="Comprehensive analysis"):
                                
                                result = await agent.analyze_drug(sample_state)
                                
                                assert "drug_analysis" in result
                                assert "drug_properties" in result
                                assert "mechanism_of_action" in result
                                assert "pharmacokinetics" in result
                                assert "drug_interactions" in result
                                assert "repurposing_potential" in result
                                assert result["drug_analysis"] == "Comprehensive analysis"
    
    @pytest.mark.asyncio
    async def test_analyze_drug_no_molecule(self, agent, sample_state_no_molecule):
        """Test drug analysis without specified molecule"""
        
        with patch.object(agent, '_extract_molecule_from_query', return_value=""):
            result = await agent.analyze_drug(sample_state_no_molecule)
            
            assert result["drug_analysis"] == "No specific drug identified for detailed analysis"
            assert result["drug_properties"] == {}
            assert result["mechanism_of_action"] == ""
            assert result["pharmacokinetics"] == ""
            assert result["drug_interactions"] == []
            assert result["repurposing_potential"] == ""
    
    @pytest.mark.asyncio
    async def test_extract_molecule_from_query(self, agent):
        """Test molecule extraction from query"""
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = "aspirin"
        
        with patch.object(agent.llm, 'ainvoke', return_value=mock_response):
            result = await agent._extract_molecule_from_query("aspirin for heart disease")
            assert result == "aspirin"
    
    @pytest.mark.asyncio
    async def test_extract_molecule_none_found(self, agent):
        """Test molecule extraction when none found"""
        
        # Mock LLM response
        mock_response = MagicMock()
        mock_response.content = "none"
        
        with patch.object(agent.llm, 'ainvoke', return_value=mock_response):
            result = await agent._extract_molecule_from_query("general cardiovascular treatments")
            assert result == ""
    
    def test_extract_therapeutic_class(self, agent):
        """Test therapeutic class extraction"""
        
        analysis_text = "This drug is an NSAID that works by inhibiting COX enzymes"
        result = agent._extract_therapeutic_class(analysis_text)
        assert result == "NSAID"
        
        analysis_text_unknown = "This is a novel compound with unknown mechanism"
        result = agent._extract_therapeutic_class(analysis_text_unknown)
        assert result == "Unknown"
    
    def test_extract_indications(self, agent):
        """Test indication extraction"""
        
        analysis_text = "Used for treating pain, inflammation, and cardiovascular disease prevention"
        result = agent._extract_indications(analysis_text)
        assert "pain" in result
        assert "inflammation" in result
        assert "cardiovascular disease" in result
        assert len(result) <= 3  # Should return max 3 indications
    
    def test_parse_interactions(self, agent):
        """Test drug interaction parsing"""
        
        interaction_text = "Significant interaction with warfarin due to increased bleeding risk. CYP enzyme interactions possible."
        result = agent._parse_interactions(interaction_text)
        
        assert len(result) >= 1
        # Check if warfarin interaction is detected
        warfarin_found = any(interaction["drug"] == "Warfarin" for interaction in result)
        assert warfarin_found