from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from tempfile import TemporaryDirectory
import logging
import time
from typing import Any, Dict, List, cast
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.graph.workflow import build_workflow_graph
from backend.graph.workflow import WorkflowState
from backend.config import (
    CORS_ALLOWED_ORIGINS,
    ENABLE_ARCHIVE_RUNS,
    ENABLE_LIVE_APIS,
    MAX_UPLOAD_BYTES,
    get_live_connector_status,
    get_live_mode_warnings,
)
from backend.models.api_models import (
    ArchivesResponse,
    DataSources,
    HealthResponse,
    Metrics,
    RunResponse,
    TimingMetrics,
)
from backend.utils.storage_utils import read_archive_entries

@asynccontextmanager
async def lifespan(_: FastAPI):
    for warning in get_live_mode_warnings():
        logger.warning("[startup] %s", warning)
    yield


app = FastAPI(title="VHS Drug Repurposing API", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
workflow_app = build_workflow_graph()
logger = logging.getLogger(__name__)


def _report_url_from_path(report_path: str) -> str | None:
    path = Path(report_path) if report_path else None
    if not path:
        return None
    return f"/reports/{path.name}"


def _save_uploaded_files(tmp_dir: Path, uploaded_files: List[UploadFile | str | None]) -> List[str]:
    saved_paths: List[str] = []
    for file in uploaded_files:
        if file is None:
            continue

        if isinstance(file, str):
            # Swagger may send an empty string for untouched file rows.
            if not file.strip():
                continue
            raise HTTPException(status_code=400, detail="Invalid file payload; upload PDF files only")

        if not isinstance(file, UploadFile):
            raise HTTPException(status_code=400, detail="Invalid file payload; upload PDF files only")

        if not file.filename:
            continue
        safe_filename = Path(file.filename).name
        if not safe_filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail=f"Only PDF uploads are supported: {safe_filename}")

        path = tmp_dir / safe_filename
        data = file.file.read()
        if len(data) > MAX_UPLOAD_BYTES:
            raise HTTPException(status_code=413, detail=f"File too large: {safe_filename}")
        path.write_bytes(data)
        saved_paths.append(str(path))
    return saved_paths


@app.get("/health")
def health() -> HealthResponse:
    mode = "live" if ENABLE_LIVE_APIS else "mock"
    return HealthResponse(status="ok", mode=mode, warnings=get_live_mode_warnings())


@app.get("/reports/{report_name}")
def download_report(report_name: str) -> FileResponse:
    safe_name = Path(report_name).name
    report_path = (Path(__file__).resolve().parent / "archives" / "reports" / safe_name).resolve()

    if not report_path.exists() or report_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=404, detail="Report not found")

    return FileResponse(path=report_path, media_type="application/pdf", filename=safe_name)


@app.post("/run", response_model=RunResponse)
def run_pipeline(
    query: str = Form(...),
    files: List[UploadFile | str | None] = File(default=[]),
) -> RunResponse:
    normalized_query = (query or "").strip()
    if not normalized_query:
        raise HTTPException(status_code=422, detail="Query must not be empty")

    request_id = str(uuid4())

    with TemporaryDirectory(prefix="vhs-run-") as temp_dir:
        request_start = time.perf_counter()
        tmp_path = Path(temp_dir)
        uploaded_pdf_paths = _save_uploaded_files(tmp_path, files)
        live_warnings = get_live_mode_warnings()
        connector_status = get_live_connector_status()

        initial_state: WorkflowState = {
            "request_id": request_id,
            "query": normalized_query,
            "logs": [f"[guard] {warning}" for warning in live_warnings],
            "trials": [],
            "patents": [],
            "fto_risk": "unknown",
            "internal_insights": [],
            "web_findings": [],
            "uploaded_pdf_paths": uploaded_pdf_paths,
            "use_live_apis": ENABLE_LIVE_APIS,
            "archive_run": ENABLE_ARCHIVE_RUNS,
        }

        final_state = cast(WorkflowState, workflow_app.invoke(initial_state))

        trials = final_state.get("trials", []) or []
        patents = final_state.get("patents", []) or []
        web_findings = final_state.get("web_findings", []) or []
        internal_insights = final_state.get("internal_insights", [])
        use_live_apis = bool(initial_state.get("use_live_apis", False))
        agent_errors = final_state.get("agent_errors", {})
        if not isinstance(agent_errors, dict):
            agent_errors = {}

        agent_metrics = final_state.get("agent_metrics", {})
        if not isinstance(agent_metrics, dict):
            agent_metrics = {}

        request_duration_ms = round((time.perf_counter() - request_start) * 1000.0, 3)

        if isinstance(internal_insights, str):
            internal_doc_count = 0 if "no internal documents" in internal_insights.lower() else 1
        else:
            internal_doc_count = len(internal_insights)

        return RunResponse(
            request_id=request_id,
            summary=final_state.get("summary", ""),
            report_path=final_state.get("report_path", ""),
            report_url=_report_url_from_path(final_state.get("report_path", "")),
            molecule=final_state.get("molecule"),
            indication=final_state.get("indication"),
            master_confidence=final_state.get("master_confidence", "unknown"),
            query_plan=final_state.get("query_plan", []),
            fto_risk=final_state.get("fto_risk", "unknown"),
            risk_assumptions=final_state.get("risk_assumptions", []),
            agent_errors=agent_errors,
            metrics=Metrics(
                trial_count=len(trials),
                patent_count=len(patents),
                web_finding_count=len(web_findings) if isinstance(web_findings, list) else 1,
                internal_insight_count=internal_doc_count,
            ),
            timing_metrics=TimingMetrics(
                request_duration_ms=request_duration_ms,
                agents=agent_metrics,
            ),
            data_sources=DataSources(
                trials="clinicaltrials.gov api v2" if use_live_apis else "backend/data/trials.csv",
                patents=(
                    "serpapi google_patents"
                    if use_live_apis and connector_status.get("serpapi_patents", False)
                    else "backend/data/patents.csv"
                ),
                guidelines=(
                    "tavily search"
                    if use_live_apis and connector_status.get("tavily", False)
                    else "backend/data/guidelines.json"
                ),
                internal_docs_uploaded=internal_doc_count > 0,
            ),
            logs=final_state.get("logs", []),
        )


@app.get("/archives")
def get_archives() -> ArchivesResponse:
    runs = read_archive_entries()
    for run in runs:
        report_path = str(run.get("report_path") or "")
        run["report_url"] = _report_url_from_path(report_path)
    return ArchivesResponse(runs=runs)
