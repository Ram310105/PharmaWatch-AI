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
# API Key
# =====================================================

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError(
        "GROQ_API_KEY not found. Check your .env file."
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
