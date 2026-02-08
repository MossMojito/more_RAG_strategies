# 🏆 AIS Sport RAG (Advanced Strategies)

This project demonstrates **Advanced RAG Strategies** for a Sports Package Assistant.
It moves beyond simple "Semantic Search" to implement **Hierarchical Retrieval** and **Context-Aware Query Rewriting** (V3 Logic).

> **Note**: This project uses a **Minimal Perfect Dataset** (consisting only of **NBA** and **Play Ultimate** packages) to clearly demonstrate the *logic* of the strategies without the noise of a full database.

---

## 🚀 Key Strategies Implemented

### 1. Context-Aware Rewriting (V3 Logic)
Instead of independent LLM calls, we use a **Combined Analysis** approach:
- **One LLM Call** performs:
    1.  **Rewrite**: Converts vague queries (e.g., "price?") into standalone queries ("price of NBA?").
    2.  **Sport Locking**: Detects if the user is asking about a specific sport (e.g., NBA) and "locks" the context.
    3.  **Topic Tracking**: Tracks the **Intent** (e.g., Pricing, Promotion) so the conversation flows naturally even when switching sports.

### 2. Hierarchical Retrieval (Parent-Child)
A common RAG failure is retrieving small chunks that lose broad context. We solve this with **Parent-Child Indexing**:
- **Child Chunks**: Small, specific text (e.g., "NBA is in Ultimate").
- **Parent Document**: The full package details (Channels, Streaming Services, Terms).
- **Strategy**: When a search hits a *Child* chunk, the engine automatically fetches the **Full Parent Document** for the LLM.
    - *Result*: The bot understands that "Play Ultimate" includes *both* NBA and Netflix/Disney+, not just the sport mentioned in the chunk.

---

## 🛠️ Architecture

1.  **Ingestion (`src/ingestion`)**:
    - Splits generic files into chunks.
    - specialized splitting for **Multi-Sport Packages** (Parent) -> Sport-Specific Sections (Children).
2.  **Engine (`src/chatbot`)**:
    - **CombinedRewriter**: Manages state (Sport/Intent) and rewrites queries.
    - **RAGEngine**: Orchestrates retrieval, using state to filter and fetch Parents.
3.  **UI (`app.py`)**:
    - Simple Gradio interface to demonstrate the chat.

## 📦 Project Structure

```
.
├── 📦 pyproject.toml           # Dependency Management
├── 🚀 app.py                   # Gradio UI Entry Point
├── 📜 verify_ingestion.py      # Data Ingestion Verification
├── 📜 verify_chat.py           # End-to-End logic Verification
├── 📂 data/                    # Data Storage
│   └── synthetic_raw/          # Clean Markdown Files (Portfolio Ready)
├── 📂 src/ais_rag/             # Core Application Source Code
│   ├── ⚙️ ingestion/           # Data Processing
│   │   ├── hierarchy.py        # Parent-Child Logic (Key Feature)
│   │   ├── chunker.py          # Smart Chunking
│   │   └── vector_store.py     # ChromaDB wrapper
│   └── 🧠 chatbot/             # AI Logic
│       ├── engine.py           # Orchestrator
│       ├── rewriter.py         # Query Rewriting Module
│       ├── memory.py           # Summary Memory Implementation
│       └── llm_client.py       # Generic LLM Client
└── 📄 requirements.txt         # Dependencies
```

## 🚀 How to Run

1.  **Clone & Install**:
    ```bash
    git clone <repo>
    cd more_RAG_strategies
    pip install -r requirements.txt
    ```

2.  **Configure**:
    - Copy `.env.example` to `.env`
    - Add your `OPENAI_API_KEY`

3.  **Ingest Data** (Builds the Vector DB):
    ```bash
    python verify_ingestion.py
    ```

4.  **Run Chat**:
    ```bash
    python app.py
    ```
    Open http://127.0.0.1:7860

## 🧪 Verified Scenarios

This codebase is verified to handle:
1.  **"How much is it?"** (after talking about NBA) -> Rewrites to "How much is NBA?".
2.  **"What about Ultimate?"** -> Switches context, retrieves Full Parent Doc (listing all apps).
3.  **"Does it have Netflix?"** -> Correctly answers YES because Parent Doc was retrieved.

---
*Based on logic from `260114_ais_sport7.ipynb` (V3)*
## 🚀 How to Run (Portfolio Demo)

1.  **Install**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Verify Ingestion**:
    Run `python verify_ingestion.py`.
    *Output*: You will see it Chunk -> Index -> Store in ChromaDB.

3.  **Run Chatbot**:
    ```bash
# Set your OpenAI API Key (or compatible endpoint)
    export OPENAI_API_KEY="sk-..."
    python app.py
    ```

## 🧠 Key Engineering Strategies

### 1. Query Rewriting (`rewriter.py`)
Users often say "And the other one?". The system uses an LLM call to rewrite this to "And the [Premier League] package?" before searching.

### 2. Intent Routing (`router.py`)
If a user asks "Show me NBA prices", the Router detects "Sports: NBA" and **hard-filters** the Vector Search to only look at NBA documents, reducing hallucinations from other sports.

### 3. Parent-Child Indexing (`hierarchy.py`)
We search on small, specific chunks (e.g., "NBA Price") but retrieved the **entire** Parent Document (the full pricing table) to ensure the LLM has complete context to answer complex questions.

### 4. Summary Memory (`memory.py`)
Instead of keeping 20 raw messages (expensive), the system periodically summarizes the conversation (e.g., "User is looking for a cheap football package") and injects this summary into the system prompt.
