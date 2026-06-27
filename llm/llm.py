import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq

# =====================================================
# Load Environment Variables
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE, override=True)

# =====================================================
# API Keys
# =====================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not found. Check your .env file."
    )

# Dedicated key for the Drug Alternatives Agent, kept separate
# so its calls don't compete with the main Event/Research/Risk
# pipeline's rate limits. Falls back to the primary key if not set.
GROQ_API_KEY_ALTERNATIVES = (
    os.getenv("GROQ_API_KEY_ALTERNATIVES") or GROQ_API_KEY
)

# =====================================================
# Model Configuration
# =====================================================

GROQ_MODEL = "llama-3.1-8b-instant"

# =====================================================
# LLM
# =====================================================

llm = ChatGroq(
    api_key=GROQ_API_KEY,
    model=GROQ_MODEL,
    temperature=0,
    max_retries=2,
)

# Separate LLM instance for the Drug Alternatives Agent.
# Uses its own key (see above) so a busy main pipeline can't
# starve Drug Alternatives of requests, and vice versa.
llm_alternatives = ChatGroq(
    api_key=GROQ_API_KEY_ALTERNATIVES,
    model=GROQ_MODEL,
    temperature=0,
    max_retries=2,
)