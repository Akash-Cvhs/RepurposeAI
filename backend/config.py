import os
from pathlib import Path

# LLM Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Backend Configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "localhost")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", 8000))
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# File Paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
ARCHIVES_DIR = BASE_DIR / "archives"
REPORTS_DIR = ARCHIVES_DIR / "reports"
RUNS_INDEX_FILE = ARCHIVES_DIR / "runs.json"
VECTORSTORE_DIR = BASE_DIR / "vectorstore" / "faiss_index"

# Data Files
TRIALS_CSV = DATA_DIR / "trials.csv"
PATENTS_CSV = DATA_DIR / "patents.csv"
GUIDELINES_JSON = DATA_DIR / "guidelines.json"

# Ensure directories exist
ARCHIVES_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Agent Configuration
DEFAULT_LLM_MODEL = "gpt-4"
MAX_ITERATIONS = 10
TIMEOUT_SECONDS = 300