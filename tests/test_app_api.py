from fastapi.testclient import TestClient
from pathlib import Path

import backend.app as app_module

app = app_module.app


def test_run_endpoint_returns_structured_metrics() -> None:
    app_module.ENABLE_ARCHIVE_RUNS = False
    client = TestClient(app)

    response = client.post(
        "/run",
        data={"query": "metformin for breast cancer"},
    )

    assert response.status_code == 200
    payload = response.json()

    assert "request_id" in payload
    assert "summary" in payload
    assert "report_path" in payload
    assert "report_url" in payload
    assert str(payload["report_url"]).startswith("/reports/")
    assert "query_plan" in payload
    assert "master_confidence" in payload
    assert "metrics" in payload
    assert "timing_metrics" in payload
    assert payload["timing_metrics"]["request_duration_ms"] >= 0
    assert isinstance(payload["timing_metrics"]["agents"], dict)
    assert "agent_errors" in payload
    assert isinstance(payload["agent_errors"], dict)
    assert payload["metrics"]["trial_count"] >= 0
    assert payload["metrics"]["patent_count"] >= 0
    assert "data_sources" in payload
    expected_trials_source = (
        "clinicaltrials.gov api v2" if app_module.ENABLE_LIVE_APIS else "backend/data/trials.csv"
    )
    assert payload["data_sources"]["trials"] == expected_trials_source
    assert "risk_assumptions" in payload


def test_run_endpoint_rejects_empty_query() -> None:
    client = TestClient(app)
    response = client.post("/run", data={"query": "   "})
    assert response.status_code == 422


def test_run_endpoint_rejects_non_pdf_upload() -> None:
    client = TestClient(app)
    response = client.post(
        "/run",
        data={"query": "metformin for breast cancer"},
        files={"files": ("notes.txt", b"not a pdf", "text/plain")},
    )
    assert response.status_code == 400


def test_report_download_endpoint_serves_pdf() -> None:
    app_module.ENABLE_ARCHIVE_RUNS = False
    client = TestClient(app)

    run_response = client.post(
        "/run",
        data={"query": "metformin for breast cancer"},
    )
    assert run_response.status_code == 200
    payload = run_response.json()

    report_path = Path(payload["report_path"])
    report_name = report_path.name
    download_response = client.get(f"/reports/{report_name}")

    assert download_response.status_code == 200
    assert download_response.headers.get("content-type", "").startswith("application/pdf")
