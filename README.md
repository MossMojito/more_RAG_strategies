# AIS Sport RAG (Refactored)

A professional, modular Retrieval-Augmented Generation (RAG) system for AIS Sports packages.
This project showcases advanced RAG techniques including Optical Character Recognition (OCR), Hierarchical Indexing, and Manual Memory Management.

## 🌟 Key Features

### 1. OCR-Enhanced Scraping
- Separate module `src/ais_rag/scraper/ocr_engine.py` using **Qwen2.5-VL**.
- Extracts text from package images, diagrams, and promotion banners.

### 2. Hierarchical RAG (Parent-Child)
- Logic in `src/ais_rag/ingestion/hierarchy.py`.
- Multi-Sport packages (PLAY SPORTS/ULTIMATE) are indexed as "Parent" documents.
- Searches hit specifically crafted "Child" chunks, but retrieve the full "Parent" context for the LLM.

### 3. Hand-Crafted Memory
- Pure Python implementation in `src/ais_rag/chatbot/memory.py`.
- Manually manages context window and history without external frameworks like LangChain.

### 4. Databricks Ready
- Designed to run on Databricks with `src/ais_rag/chatbot/llm_client.py` wrapping the Model Serving Endpoint.

## 📂 Project Structure

```
ais-sport-rag/
├── app.py                  # Main Gradio Application
├── src/ais_rag/            # Main Package
│   ├── config.py           # Central Configuration
│   ├── scraper/            # Crawl4AI + OCR
│   ├── ingestion/          # Chunking + VectorDB
│   └── chatbot/            # RAG Engine + Memory
├── notebooks/              # Demos (OCR, RAG)
└── requirements.txt
```

> [!NOTE]
> **Portfolio Context**: 
> Real user data and scraped content contain confidential information and have been excluded.
> This repository includes **mock data** (`data/raw/*.md`) to demonstrate the ingestion pipeline and RAG architecture functionality.

## 🚀 Usage

### 1. Setup
```bash
pip install -r requirements.txt
```

### 2. Run Ingestion (Demo Mode)
We provide mock data to demonstrate the hierarchical indexing logic.
Open `notebooks/demo_ingestion.ipynb` and run all cells. This will:
1. Load the mock Markdown files.
2. Generate Parent-Child chunks.
3. Create a local ChromaDB vector store in `data/vectordb`.

### 3. Run the Chatbot
Once ingestion is complete, launch the interface:

```bash
# Set dummy keys if testing locally without LLM connection
export DATABRICKS_TOKEN="dummy"
export DATABRICKS_ENDPOINT="http://localhost:8000"

python app.py
```
*Note: Without a valid LLM endpoint, the bot will error on generation but the UI and Retrieval logic will function.*
