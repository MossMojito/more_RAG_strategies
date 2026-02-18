import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ===== PATHS =====
# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "synthetic_raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
VECTOR_DB_DIR = DATA_DIR / "vectordb"

# Create directories if they don't exist
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
VECTOR_DB_DIR.mkdir(parents=True, exist_ok=True)

# ===== RAG SETTINGS =====
K_CHUNKS = 5
MAX_LLM_TOKENS = 3000
CHUNK_SIZE = 3000
CHUNK_OVERLAP = 800

# ===== SPORT MAPPINGS =====
AVAILABLE_SPORTS = {
    "NBA": "🏀 บาสเก็ตบอล (NBA)",
    "MULTI": "🏆 ยูนิเวอร์แซล (Ultimate)"
}

# Mapping from package names to specific sports or 'MULTI'
PACKAGE_TO_SPORT = {
    "ULTIMATE": "MULTI",
    "NBA": "NBA"
}

# Synonyms/Variations for sport detection
SPORT_NAMES = {
    "NBA": ["NBA", "บาสเก็ตบอล", "BASKETBALL"],
    "MULTI": ["ULTIMATE", "ULTIMATE", "ทุกกีฬา"]
}

# Reference Mapping for Parent-Child Ingestion Logic
# (These files are conceptual examples for the hierarchy.py module)
FILE_TO_SPORT_MAPPING = {
    "nba_package.md": {"sports": ["NBA"], "is_multi_sport": False},
    "ultimate_package.md": {
        "sports": ["EPL", "GOLF", "NBA", "NFL", "TENNIS"],
        "is_multi_sport": True
    },
}
