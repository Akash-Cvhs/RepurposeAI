from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent
ROOT_DIR = BACKEND_DIR.parent
load_dotenv(ROOT_DIR / ".env")


def _get_int_env(name: str, default: int) -> int:
	raw = os.getenv(name)
	if raw is None:
		return default
	try:
		return int(raw)
	except ValueError:
		return default


def _get_bool_env(name: str, default: bool) -> bool:
	raw = os.getenv(name)
	if raw is None:
		return default
	return raw.strip().lower() in {"1", "true", "yes", "on"}


def _get_list_env(name: str, default: list[str]) -> list[str]:
	raw = os.getenv(name)
	if raw is None:
		return default
	parts = [item.strip() for item in raw.split(",") if item.strip()]
	return parts or default


def _get_choice_env(name: str, default: str, allowed: set[str]) -> str:
	raw = os.getenv(name)
	if raw is None:
		return default
	value = raw.strip().lower()
	return value if value in allowed else default

DATA_DIR = BACKEND_DIR / "data"
ARCHIVES_DIR = BACKEND_DIR / "archives"
REPORTS_DIR = ARCHIVES_DIR / "reports"
RUNS_INDEX_PATH = ARCHIVES_DIR / "runs.json"

TRIALS_CSV_PATH = DATA_DIR / "trials.csv"
PATENTS_CSV_PATH = DATA_DIR / "patents.csv"
GUIDELINES_JSON_PATH = DATA_DIR / "guidelines.json"

CLINICAL_TRIALS_API_URL = os.getenv(
	"CLINICAL_TRIALS_API_URL", "https://clinicaltrials.gov/api/v2/studies"
)
CLINICAL_TRIALS_PAGE_SIZE = _get_int_env("CLINICAL_TRIALS_PAGE_SIZE", 20)
CLINICAL_TRIALS_TIMEOUT_SECONDS = _get_int_env("CLINICAL_TRIALS_TIMEOUT_SECONDS", 20)

TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TAVILY_API_URL = os.getenv("TAVILY_API_URL", "https://api.tavily.com/search")
TAVILY_TIMEOUT_SECONDS = _get_int_env("TAVILY_TIMEOUT_SECONDS", 20)
TAVILY_MAX_RESULTS = _get_int_env("TAVILY_MAX_RESULTS", 5)

SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
SERPAPI_API_URL = os.getenv("SERPAPI_API_URL", "https://serpapi.com/search")
SERPAPI_TIMEOUT_SECONDS = _get_int_env("SERPAPI_TIMEOUT_SECONDS", 20)
SERPAPI_MAX_RESULTS = _get_int_env("SERPAPI_MAX_RESULTS", 10)
SERPAPI_ENGINE = os.getenv("SERPAPI_ENGINE", "google_patents")

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "none").lower()
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_BASE_URL = os.getenv("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_TIMEOUT_SECONDS = _get_int_env("GROQ_TIMEOUT_SECONDS", 30)

ENABLE_LIVE_APIS = _get_bool_env("ENABLE_LIVE_APIS", False)
ENABLE_ARCHIVE_RUNS = _get_bool_env("ENABLE_ARCHIVE_RUNS", True)
CORS_ALLOWED_ORIGINS = _get_list_env(
	"CORS_ALLOWED_ORIGINS",
	["http://localhost:5173", "http://127.0.0.1:5173"],
)

MAX_UPLOAD_BYTES = _get_int_env("MAX_UPLOAD_BYTES", 10 * 1024 * 1024)

HTTP_MAX_RETRIES = _get_int_env("HTTP_MAX_RETRIES", 2)
HTTP_RETRY_BACKOFF_SECONDS = _get_int_env("HTTP_RETRY_BACKOFF_SECONDS", 1)
HTTP_CIRCUIT_BREAKER_THRESHOLD = _get_int_env("HTTP_CIRCUIT_BREAKER_THRESHOLD", 3)
HTTP_CIRCUIT_RESET_SECONDS = _get_int_env("HTTP_CIRCUIT_RESET_SECONDS", 30)

PDF_LAYOUT_MODE = _get_choice_env("PDF_LAYOUT_MODE", "dense", {"dense", "presentation"})


def get_live_connector_status() -> dict[str, bool]:
	"""Return per-connector readiness flags for live mode guardrails."""
	return {
		"clinical_trials": True,
		"tavily": bool(TAVILY_API_KEY),
		"serpapi_patents": bool(SERPAPI_API_KEY),
		"groq": LLM_PROVIDER == "groq" and bool(GROQ_API_KEY),
	}


def get_live_mode_warnings() -> list[str]:
	"""Return startup/run warnings to avoid mock/live confusion."""
	if not ENABLE_LIVE_APIS:
		return ["Live APIs are disabled; all connectors use local mock fallback sources."]

	status = get_live_connector_status()
	warnings: list[str] = []

	if not status["tavily"]:
		warnings.append("Tavily key missing; web intelligence will fallback to backend/data/guidelines.json.")
	if not status["serpapi_patents"]:
		warnings.append("SerpAPI key missing; patent landscape will fallback to backend/data/patents.csv.")
	if not status["groq"]:
		warnings.append("Groq not fully configured; internal insights summarization will use deterministic fallback.")

	if warnings:
		warnings.insert(0, "Live mode enabled with partial connector readiness.")
		return warnings

	return ["Live mode enabled; all configured connectors are ready."]
