import os
from pathlib import Path

# ===== PATHS =====
# Get the project root directory (2 levels up from this file)
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
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
    "EPL": "⚽ พรีเมียร์ลีก (EPL)",
    "NBA": "🏀 บาสเก็ตบอล (NBA)",
    "NFL": "🏈 อเมริกันฟุตบอล (NFL)",
    "TENNIS": "🎾 เทนนิส (Tennis)",
    "GOLF1": "⛳ กอล์ฟ 1 (Golf 1)",
    "GOLF2": "⛳ กอล์ฟ 2 (Golf 2)",
}

# Mapping from package names to specific sports or 'MULTI'
PACKAGE_TO_SPORT = {
    "MONOMAX": "EPL",
    "MONOMAX STANDARD": "EPL",
    "PLAY SPORTS": "MULTI",
    "PLAY SPORT": "MULTI",
    "PLAY ULTIMATE": "MULTI",
}

# Synonyms/Variations for sport detection
SPORT_NAMES = {
    "EPL": ["EPL", "ฟุตบอล", "พรีเมียร์ลีก", "PREMIER LEAGUE", "FOOTBALL", "MONOMAX"],
    "NBA": ["NBA", "บาสเก็ตบอล", "BASKETBALL"],
    "NFL": ["NFL", "อเมริกันฟุตบอล", "AMERICAN FOOTBALL"],
    "TENNIS": ["TENNIS", "เทนนิส", "ATP"],
    "GOLF1": ["GOLF1", "GOLF", "กอล์ฟ", "PGA", "LPGA"],
    "GOLF2": ["GOLF2", "GOLF", "กอล์ฟ", "PGA", "LPGA"],
}

# Manual file mapping for ingestion
FILE_TO_SPORT_MAPPING = {
    "final_EPL_clean.md": {"sports": ["EPL"], "is_multi_sport": False},
    "final_GOLF1_clean.md": {"sports": ["GOLF"], "is_multi_sport": False},
    "final_GOLF2_clean.md": {"sports": ["GOLF"], "is_multi_sport": False},
    "final_NBA_clean.md": {"sports": ["NBA"], "is_multi_sport": False},
    "final_NFL_clean.md": {"sports": ["NFL"], "is_multi_sport": False},
    "final_TENNIS_clean.md": {"sports": ["TENNIS"], "is_multi_sport": False},
    "final_PLAY_SPORTS_clean.md": {
        "sports": ["EPL", "GOLF", "NBA", "NFL", "TENNIS"],
        "is_multi_sport": True
    },
    "final_PLAY_ULTIMATE_clean.md": {
        "sports": ["EPL", "GOLF", "NBA", "NFL", "TENNIS"],
        "is_multi_sport": True
    },
}
