# 🏆 SportStream RAG (Advanced Strategies)

This project demonstrates **Advanced RAG Strategies** for a Sports Package Assistant.
It moves beyond simple "Semantic Search" to implement **Hierarchical Retrieval** and **Context-Aware Query Rewriting** (V3 Logic).

> **Note**: This project uses a **Minimal Perfect Dataset** concept to clearly demonstrate the *logic* of the strategies.

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
