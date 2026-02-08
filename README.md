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

## 📦 Repository Structure

This repository is a **Reference Implementation** of advanced RAG techniques.

```text
.
├── 📂 data/
│   └── synthetic_raw/       # Minimal Perfect Dataset (NBA + Ultimate)
│   └── processed/           # Structure for Parent-Child relationships
├── 📂 src/ais_rag/          # Core Logic
│   ├── ⚙️ ingestion/
│   │   ├── hierarchy.py     # [CRITICAL] Implements Parent-Child splitting logic
│   │   ├── chunker.py       # Markdown chunking strategy
│   │   └── vector_store.py  # Vector DB Abstraction
│   └── 🧠 chatbot/
│       ├── rewriter.py      # [CRITICAL] V3 Combined Analysis (Rewrites + Intent)
│       ├── engine.py        # [CRITICAL] State Management & Retrieval Orchestration
│       ├── memory.py        # Conversation Summary implementation
│       └── llm_client.py    # LLM Interface
├── 🚀 app.py                # Reference UI Implementation (Gradio)
└── 📄 requirements.txt      # Technology Stack
```

## 🧠 Key Engineering Patterns

### 1. Unified Analysis Architecture (`rewriter.py`)
Instead of chaining multiple LLM calls (latency heavy), we use a single purpose-built prompt to:
*   **Rewrite** the user query.
*   **Detect Sport** context (e.g., "NBA").
*   **Identify Intent** (e.g., "Price", "Package Details").
*   **Return JSON** for deterministic routing.

### 2. Sticky Context Management (`engine.py`)
The system implements a "Sticky State" separate from the conversation history.
*   *User*: "How much is NBA?" -> **State Locked**: `Sport=NBA`
*   *User*: "What about the other one?" -> **Rewriter** sees state -> **Rewrite**: "What about [NBA] other options?"

### 3. Hierarchical Retrieval (`hierarchy.py`)
**Problem**: Vector search retrieves small fragments (Children) that lack context.
**Solution**:
1.  **Index**: Small, specific chunks (e.g., "EPL Price is 299").
2.  **Retrieve**: When a chunk is hit, the system fetches the **Parent Document** (Full Package Table).
3.  **Generate**: The LLM receives the full context, ensuring it knows that "Play Ultimate" contains both EPL and NBA.

---
*This project strictly demonstrates the architectural implementation of V3 RAG Logic as defined in `260114_ais_sport7.ipynb`.*

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
