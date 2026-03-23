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
        DEFAULT_LLM_MODEL = "llama-3.3-70b-versatile"  # Groq model
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

# JWT Authentication
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "change-this-secret-key-in-production")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", 1440))  # 24 hours

# Rate Limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv("RATE_LIMIT_PER_MINUTE", 60))
RATE_LIMIT_PER_HOUR = int(os.getenv("RATE_LIMIT_PER_HOUR", 1000))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vhs_drug_db.sqlite")
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# External API Configuration
ENABLE_LIVE_APIS = os.getenv("ENABLE_LIVE_APIS", "false").lower() == "true"

# Clinical Trials API
CLINICAL_TRIALS_API_URL = os.getenv(
    "CLINICAL_TRIALS_API_URL",
    "https://clinicaltrials.gov/api/v2/studies"
)
CLINICAL_TRIALS_PAGE_SIZE = int(os.getenv("CLINICAL_TRIALS_PAGE_SIZE", 50))
CLINICAL_TRIALS_TIMEOUT_SECONDS = int(os.getenv("CLINICAL_TRIALS_TIMEOUT_SECONDS", 30))

# Patent Search API (SerpAPI)
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
SERPAPI_API_URL = os.getenv("SERPAPI_API_URL", "https://serpapi.com/search")
SERPAPI_ENGINE = os.getenv("SERPAPI_ENGINE", "google_patents")
SERPAPI_MAX_RESULTS = int(os.getenv("SERPAPI_MAX_RESULTS", 50))
SERPAPI_TIMEOUT_SECONDS = int(os.getenv("SERPAPI_TIMEOUT_SECONDS", 30))

# Web Intelligence API (Tavily)
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
TAVILY_API_URL = os.getenv("TAVILY_API_URL", "https://api.tavily.com/search")
TAVILY_MAX_RESULTS = int(os.getenv("TAVILY_MAX_RESULTS", 10))

# CSV Data Paths (fallback when APIs unavailable)
TRIALS_CSV_PATH = DATA_DIR / "trials.csv"
PATENTS_CSV_PATH = DATA_DIR / "patents.csv"