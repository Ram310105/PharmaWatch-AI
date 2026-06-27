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

# ---------------------------------------------------------
# Dedicated keys for the Drug Alternatives Agent.
#
# Kept separate from the main Research Agent's keys so that
# Drug Alternatives lookups cannot exhaust the Tavily credit
# pool (or hit Groq rate limits) that the core Event/Research/
# Risk pipeline depends on.
#
# Falls back to the primary keys if dedicated ones are not
# set, so the app still runs with a single key during local
# development.
# ---------------------------------------------------------

TAVILY_API_KEY_ALTERNATIVES = (
    os.getenv("TAVILY_API_KEY_ALTERNATIVES") or TAVILY_API_KEY
)
GROQ_API_KEY_ALTERNATIVES = (
    os.getenv("GROQ_API_KEY_ALTERNATIVES") or GROQ_API_KEY
)

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
#
# Previous query OR'd disconnected single words together
# ("war OR shipping OR port OR export OR factory ..."),
# which let NewsAPI match almost any article containing any
# ONE of those common words anywhere in its text — finance,
# sports, and tech news routinely matched "import"/"export"/
# "factory" with zero pharma relevance.
#
# This version ANDs a disruption-type clause with a pharma/
# supply-chain anchor clause, so every returned article has
# to touch BOTH a disruption signal AND a pharma/health/
# logistics signal. NewsAPI's /everything query supports
# AND, OR, NOT and parentheses grouping.

NEWS_QUERY = (
    '(war OR sanctions OR earthquake OR strike '
    'OR "export ban" OR "factory shutdown" OR "port closure") '
    'AND (pharmaceutical OR pharma OR medicine OR drug OR API '
    'OR vaccine OR insulin OR "supply chain")'
)

NEWS_LANGUAGE = "en"
NEWS_SORT_BY = "publishedAt"
NEWS_PAGE_SIZE = 40

# =====================================================
# HTTP CONFIGURATION
# =====================================================

REQUEST_TIMEOUT = 15.0

# =====================================================
# GDELT CONFIGURATION
# =====================================================
#
# Previous query was a single bare word ("war"), which GDELT
# treats as an unanchored keyword match across all global
# coverage — almost entirely unrelated to pharma supply chains
# (sports "war of words", political "war room" stories, etc).
#
# GDELT's DOC 2.0 API supports phrase search with quotes and
# boolean OR via parentheses; bare space-separated terms are
# ANDed together. This version requires a pharma/health anchor
# AND a disruption-type term to co-occur in the same article.

GDELT_BASE_URL = "https://api.gdeltproject.org/api/v2/doc/doc"
GDELT_QUERY = (
    '(pharmaceutical OR "drug supply" OR medicine OR vaccine OR insulin) '
    'AND (shortage OR shutdown OR sanctions OR "export ban" OR strike '
    'OR earthquake OR flood OR war OR disruption)'
)
# Widened from 24h: the AND-anchored query above is meaningfully
# stricter than the old bare-keyword query, so a 24h window can
# realistically return zero matches on a quiet news day. 72h gives
# enough margin for a live demo while still being "recent news".
GDELT_TIMESPAN = "72h"
GDELT_MAX_RECORDS = 40
GDELT_MODE = "ArtList"
GDELT_FORMAT = "json"

# =====================================================
# LLM CONFIGURATION
# =====================================================

GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_REASONING_MODEL = "llama-3.3-70b-versatile"