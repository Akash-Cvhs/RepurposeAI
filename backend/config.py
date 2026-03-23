import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# LLM Configuration
LLM_API_KEY = os.getenv("LLM_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or LLM_API_KEY
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

# Detect LLM provider based on API key
if LLM_API_KEY:
    if LLM_API_KEY.startswith("gsk_"):
        LLM_PROVIDER = "groq"
        DEFAULT_LLM_MODEL = "openai/gpt-oss-20b"  # Updated model
    elif LLM_API_KEY.startswith("sk-"):
        LLM_PROVIDER = "openai"
        DEFAULT_LLM_MODEL = "gpt-4"
    elif LLM_API_KEY.startswith("sk-ant-"):
        LLM_PROVIDER = "anthropic"
        DEFAULT_LLM_MODEL = "claude-3-5-sonnet-20241022"
    else:
        LLM_PROVIDER = "openai"  # default
        DEFAULT_LLM_MODEL = "gpt-4"
else:
    LLM_PROVIDER = "openai"
    DEFAULT_LLM_MODEL = "gpt-4"

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
MOLECULE_IMAGES_DIR = ARCHIVES_DIR / "molecule_images"

# Data Files
TRIALS_CSV = DATA_DIR / "trials.csv"
PATENTS_CSV = DATA_DIR / "patents.csv"
GUIDELINES_JSON = DATA_DIR / "guidelines.json"

# Ensure directories exist
ARCHIVES_DIR.mkdir(exist_ok=True)
REPORTS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
MOLECULE_IMAGES_DIR.mkdir(exist_ok=True)

# Agent Configuration
MAX_ITERATIONS = 10
TIMEOUT_SECONDS = 300