# 📚 Product Catalog RAG (Advanced Architecture)

This project demonstrates **Advanced RAG Strategies** for a specific **Product Catalog AI Assistant**.
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
*   **Detect Product Category** context (e.g., "Enterprise Software").
*   **Identify Intent** (e.g., "Pricing", "Compatibility").
*   **Return JSON** for deterministic routing.

### 2. Sticky Context Management (`engine.py`)
The system implements a **Sticky State** separate from conversation history.
*   *User*: "Tell me about the Pro Plan." -> **State Locked**: `Product='Pro Plan'`
*   *User*: "What is the price?" -> **Rewriter** sees state -> **Rewrite**: "What is the price of [Pro Plan]?"

### 3. Hierarchical Retrieval (`hierarchy.py`)
**Problem**: Vector search retrieves small fragments (Children) that lack context.
**Solution**:
1.  **Index**: Small, specific chunks (e.g., "4K Support included").
2.  **Retrieve**: When a chunk is hit, the system fetches the **Parent Document** (Full Product Brochure).
3.  **Generate**: The LLM receives the full context, ensuring it knows that "Enterprise Bundle" includes specific features from multiple sub-products.

---
*This architecture is a reference implementation for complex RAG systems.*

## 🧪 Verified Scenarios

This architecture is verified to handle:
1.  **Context-Aware Price Check**:
    *   *User*: "How much is the Pro Plan?" (Context Locks to `Pro Plan`)
    *   *User*: "Does it include API access?" (System knows 'it' = Pro Plan)
2.  **Cross-Product Inquiry**:
    *   *User*: "What about the Enterprise Bundle?" (Context Switches, retrieval targets Enterprise parent doc)
3.  **Feature Lookup**:
    *   *User*: "Which plan has 24/7 support?" (Retrieves parent documents to check feature lists across products)
