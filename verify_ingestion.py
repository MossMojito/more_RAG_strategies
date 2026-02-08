import sys
import os
from pathlib import Path

# Add src to path
sys.path.append(os.path.abspath("src"))

from ais_rag.ingestion.chunker import MarkdownChunker
from ais_rag.ingestion.vector_store import VectorStore
from ais_rag.ingestion.hierarchy import create_parent_child_data
from ais_rag.config import RAW_DATA_DIR

def run_mock_ingestion():
    print("🚀 Starting Mock Ingestion...")
    
    # 1. Chunking
    chunker = MarkdownChunker()
    # Ensure raw data dir exists
    # Ensure raw data dir exists
    if not RAW_DATA_DIR.exists():
        print(f"❌ Data directory not found: {RAW_DATA_DIR}")
        return

    print(f"📂 Reading from: {RAW_DATA_DIR}")
    all_chunks = chunker.process_directory(RAW_DATA_DIR)
    
    if not all_chunks:
        print("⚠️ No chunks generated. Check your mock data files!")
        return

    # 2. Vector Store
    print("💾 Storing in ChromaDB...")
    store = VectorStore()
    store.reset() # Start fresh
    store.add_chunks(all_chunks)
    
    # 3. Verify
    count = store.count()
    print(f"✅ Success! Ingested {count} chunks into ChromaDB.")

if __name__ == "__main__":
    run_mock_ingestion()
