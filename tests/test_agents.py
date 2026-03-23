from pathlib import Path
from typing import Any, Dict

from backend.agents.clinical_trials_agent import clinical_trials_agent_node
from backend.agents.internal_insights_agent import internal_insights_agent_node
from backend.agents.patent_agent import patent_agent_node
from backend.agents.report_generator_agent import report_generator_agent_node
from backend.agents.web_intel_agent import web_intel_agent_node


def test_clinical_trials_agent_basic() -> None:
    state = {"molecule": "metformin", "indication": "breast cancer", "logs": [], "use_live_apis": False}
    new_state = clinical_trials_agent_node(state)
    assert "trials" in new_state
    assert isinstance(new_state["trials"], list)


def test_clinical_trials_agent_uses_live_api(monkeypatch) -> None:
    def fake_request_json(**kwargs):
        return {
            "studies": [
                {
                    "protocolSection": {
                        "identificationModule": {
                            "nctId": "NCT99999999",
                            "briefTitle": "Metformin in Breast Cancer",
                        },
                        "statusModule": {
                            "overallStatus": "RECRUITING",
                            "startDateStruct": {"date": "2025-01"},
                            "completionDateStruct": {"date": "2027-12"},
                        },
                        "conditionsModule": {"conditions": ["Breast Cancer"]},
                        "designModule": {"phases": ["PHASE2"]},
                        "sponsorCollaboratorsModule": {"leadSponsor": {"name": "Demo Sponsor"}},
                        "contactsLocationsModule": {
                            "locations": [{"city": "Boston", "country": "United States"}]
                        },
                    }
                }
            ]
        }

    monkeypatch.setattr("backend.agents.clinical_trials_agent.request_json", fake_request_json)

    state = {"molecule": "metformin", "indication": "breast cancer", "logs": [], "use_live_apis": True}
    new_state = clinical_trials_agent_node(state)

    assert len(new_state["trials"]) == 1
    assert new_state["trials"][0]["nct_id"] == "NCT99999999"
    assert new_state["trials"][0]["source"] == "clinicaltrials.gov"


def test_clinical_trials_agent_falls_back_to_csv(monkeypatch) -> None:
    def fake_request_json(**kwargs):
        raise RuntimeError("network unavailable")

    monkeypatch.setattr("backend.agents.clinical_trials_agent.request_json", fake_request_json)

    state = {"molecule": "metformin", "indication": "breast cancer", "logs": [], "use_live_apis": True}
    new_state = clinical_trials_agent_node(state)

    assert isinstance(new_state["trials"], list)
    assert len(new_state["trials"]) >= 1
    assert any("fallback" in log.lower() for log in new_state["logs"])


def test_patent_agent_sets_fto_risk() -> None:
    state = {"molecule": "metformin", "logs": []}
    new_state = patent_agent_node(state)
    assert "fto_risk" in new_state
    assert new_state["fto_risk"] in {"low", "medium", "high", "unknown"}


def test_patent_agent_uses_serpapi_when_available(monkeypatch) -> None:
    def fake_request_json(**kwargs):
        return {
            "patent_results": [
                {
                    "publication_number": "US20240012345A1",
                    "title": "Metformin compositions for breast cancer",
                    "snippet": "Compositions and methods for treatment of breast cancer.",
                    "publication_date": "2024-01-18",
                    "assignee": "Demo Pharma",
                    "patent_link": "https://patents.google.com/patent/US20240012345A1",
                }
            ]
        }

    monkeypatch.setattr("backend.agents.patent_agent.SERPAPI_API_KEY", "test-key")
    monkeypatch.setattr("backend.agents.patent_agent.request_json", fake_request_json)

    state = {"molecule": "metformin", "indication": "breast cancer", "logs": [], "use_live_apis": True}
    new_state = patent_agent_node(state)

    assert len(new_state["patents"]) == 1
    assert new_state["patents"][0]["source"] == "serpapi_google_patents"
    assert new_state["patents"][0]["patent_id"] == "US20240012345A1"


def test_patent_agent_fallbacks_when_serpapi_fails(monkeypatch) -> None:
    def fake_request_json(**kwargs):
        raise RuntimeError("serpapi unavailable")

    monkeypatch.setattr("backend.agents.patent_agent.SERPAPI_API_KEY", "test-key")
    monkeypatch.setattr("backend.agents.patent_agent.request_json", fake_request_json)

    state = {"molecule": "metformin", "logs": [], "use_live_apis": True}
    new_state = patent_agent_node(state)

    assert isinstance(new_state["patents"], list)
    assert len(new_state["patents"]) >= 1
    assert any("fallback" in log.lower() for log in new_state["logs"])


def test_patent_agent_parses_google_patents_organic_results(monkeypatch) -> None:
    def fake_request_json(**kwargs):
        return {
            "organic_results": [
                {
                    "patent_id": "patent/EP2264377A2/en",
                    "patent_link": "https://patents.google.com/patent/EP2264377A2/en",
                    "title": "Solar tracking module",
                    "snippet": "A module for tracking and concentrating sunlight.",
                    "publication_date": "2010-12-22",
                    "assignee": "Green Plus Co. Ltd.",
                    "publication_number": "EP2264377A2",
                }
            ]
        }

    monkeypatch.setattr("backend.agents.patent_agent.SERPAPI_API_KEY", "test-key")
    monkeypatch.setattr("backend.agents.patent_agent.request_json", fake_request_json)

    state = {"molecule": "metformin", "indication": "oncology", "logs": [], "use_live_apis": True}
    new_state = patent_agent_node(state)

    assert len(new_state["patents"]) == 1
    assert new_state["patents"][0]["patent_id"] == "EP2264377A2"
    assert new_state["patents"][0]["jurisdiction"] == "EP"


def test_internal_insights_handles_no_pdfs() -> None:
    state = {"uploaded_pdf_paths": [], "logs": []}
    new_state = internal_insights_agent_node(state)
    assert "internal_insights" in new_state
    assert isinstance(new_state["internal_insights"], str)


def test_web_intel_agent_returns_findings() -> None:
    state = {"molecule": "metformin", "indication": "breast cancer", "logs": [], "use_live_apis": False}
    new_state = web_intel_agent_node(state)
    assert "web_findings" in new_state
    assert isinstance(new_state["web_findings"], list)


def test_web_intel_agent_uses_tavily_when_available(monkeypatch) -> None:
    def fake_request_json(**kwargs):
        return {
            "results": [
                {
                    "title": "Metformin in oncology review",
                    "content": "A review discussing potential repurposing routes in breast cancer.",
                    "url": "https://example.org/metformin-oncology-review",
                }
            ]
        }

    monkeypatch.setattr("backend.agents.web_intel_agent.TAVILY_API_KEY", "test-key")
    monkeypatch.setattr("backend.agents.web_intel_agent.request_json", fake_request_json)

    state = {"molecule": "metformin", "indication": "breast cancer", "logs": [], "use_live_apis": True}
    new_state = web_intel_agent_node(state)

    assert len(new_state["web_findings"]) == 1
    assert "Tavily" in new_state["web_findings"][0]


def test_web_intel_agent_fallbacks_when_tavily_fails(monkeypatch) -> None:
    def fake_request_json(**kwargs):
        raise RuntimeError("tavily unavailable")

    monkeypatch.setattr("backend.agents.web_intel_agent.TAVILY_API_KEY", "test-key")
    monkeypatch.setattr("backend.agents.web_intel_agent.request_json", fake_request_json)

    state = {"molecule": "metformin", "indication": "breast cancer", "logs": [], "use_live_apis": True}
    new_state = web_intel_agent_node(state)

    assert isinstance(new_state["web_findings"], list)
    assert len(new_state["web_findings"]) >= 1
    assert any("mock guidelines" in log.lower() for log in new_state["logs"])


def test_report_generator_creates_pdf() -> None:
    state = {
        "query": "metformin for breast cancer",
        "molecule": "metformin",
        "indication": "breast cancer",
        "trials": [],
        "patents": [],
        "fto_risk": "medium",
        "internal_insights": "No internal documents uploaded.",
        "web_findings": [],
        "query_plan": [
            {"agent": "clinical_trials", "objective": "Fetch trial landscape", "enabled": True}
        ],
        "logs": [],
        "archive_run": False,
    }
    new_state = report_generator_agent_node(state)
    assert Path(new_state["report_path"]).exists()
    assert "summary" in new_state
    assert "risk_assumptions" in new_state
    assert isinstance(new_state["risk_assumptions"], list)
    assert "agent_errors" in new_state
