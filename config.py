import os
from pathlib import Path

from dotenv import load_dotenv

# =====================================================
# Load .env from project root
# =====================================================

BASE_DIR = Path(__file__).resolve().parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)

# =====================================================
# API KEYS
# =====================================================

NEWS_API_KEY = os.getenv("NEWS_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# =====================================================
# DEBUG (Temporary)
# =====================================================

if __name__ == "__main__":
    print("=" * 50)
    print("Environment Check")
    print("=" * 50)
    print("ENV FILE :", ENV_FILE)
    print("EXISTS   :", ENV_FILE.exists())
    print("NEWS     :", "Loaded" if NEWS_API_KEY else "NOT FOUND")
    print("GROQ     :", "Loaded" if GROQ_API_KEY else "NOT FOUND")
    print("TAVILY   :", "Loaded" if TAVILY_API_KEY else "NOT FOUND")
    print("=" * 50)

# =====================================================
# NEWS API CONFIGURATION
# =====================================================

NEWS_QUERY = (
    "war OR shipping OR port OR sanctions "
    "OR export OR import OR factory "
    "OR earthquake OR flood "
    "OR strike OR infrastructure"
)

NEWS_LANGUAGE = "en"
NEWS_SORT_BY = "publishedAt"
NEWS_PAGE_SIZE = 20

# =====================================================
# HTTP CONFIGURATION
# =====================================================

REQUEST_TIMEOUT = 15.0

# =====================================================
# GDELT CONFIGURATION
# =====================================================

GDELT_BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_QUERY = "war"
GDELT_TIMESPAN = "24h"
GDELT_MAX_RECORDS = 20
GDELT_MODE = "ArtList"
GDELT_FORMAT = "json"

# =====================================================
# LLM CONFIGURATION
# =====================================================

GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_REASONING_MODEL = "llama-3.3-70b-versatile"
