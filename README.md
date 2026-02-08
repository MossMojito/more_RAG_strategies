# 📚 Product Catalog Information RAG in Telco

This project demonstrates an **Use-case RAG Architecture** designed for Product Information Systems.

## 💡 The Use Case
Imagine you have a system with **thousands of products**. Each product has its own specific information, pricing, and details.
Instead of forcing users or staff to manually search for each **Product ID** and read through long documentation, a **Chatbot RAG** is the ideal solution to instantly retrieve answers.

### ❌ The Problem
However, simply "feeding" documents to a standard RAG chatbot often fails in this scenario:
1.  **Context Confusion**: If a user asks *"How much is it?"*, the bot doesn't know *which* product they are currently discussing.
2.  **Fragmented Answers**: The bot might find a small text chunk saying *"Includes 5G support"*, but fail to understand *which plan* that feature belongs to, leading to wrong answers.

### ✅ Our Solution (Two Distinct Strategies)
We implemented **two separate but complementary strategies** to solve these problems:

1.   **The Core: Context-Aware Query Rewriting**
     *   *Problem*: Users ask vague questions like "price?".
     *   *Solution*: The system maintains state and rewrites every query to be self-contained (e.g., "price of Pro Plan") **before** it touches the vector database. This ensures high-accuracy retrieval for *any* query.

2.   **The Add-on: Hierarchical Retrieval (Parent-Child)**
     *   *Problem*: Some products are "Bundles" of many smaller items. Finding one item doesn't explain the whole bundle.
     *   *Solution*: **Only when** a detected product is part of a hierarchy (like a Bundle), the system automatically fetches the **Parent Document** to give the LLM the full context of how items relate to each other.

---

### 🏗️ Architecture Diagram

```mermaid
flowchart TD
    subgraph Scraper ["1. OCR-Enhanced Scraping"]
        Web[Sports Website] -->|Auth & Crawl| Crawler[Crawl4AI Engine]
        Crawler -->|Raw HTML| HTML_Parse[HTML Parser]
        Crawler -->|Image URLs| OCR[Qwen2.5-VL OCR]
        OCR -->|Extracted Text| Merger[Content Merger]
        HTML_Parse --> Merger
        Merger -->|Full Markdown| RawMD[Raw Documents]
    end

    subgraph Ingestion ["2. Hierarchical Indexing"]
        RawMD -->|Split| Chunker[recursive_character_splitter]
        Chunker -->|Detect Packages| Logic{Is Multi-Sport?}
        
        Logic -- Yes --> Parent["Parent Doc (Full Context)"]
        Logic -- Yes --> Child["Child Doc (Specific Sport)"]
        Logic -- No --> Child
        
        Parent -.->|Store ID| VectorDB[(ChromaDB)]
        Child -->|Embed via E5| VectorDB
    end

    subgraph Chatbot ["3. RAG Engine Logic"]
        User[User Query] -->|Input| Memory[Conversation Memory]
        Memory -->|Context| Engine[RAG Engine Logic]
        
        %% Strategy 1: Always rewrite
        Engine -->|Step 1: Unified Analysis| Rewriter["**Combined Rewriter**<br>(Rewrite + Intent + Product)"]
        Rewriter -->|Step 2: Search| VectorDB
        
        VectorDB -->|Retrieve Hits| Hits[Top-K Chunks]
        
        %% Strategy 2: Conditional Hierarchy
        Hits --> RetrievalLogic{Is Hierarchy/Bundle?}
        RetrievalLogic -- Yes --> Parent[Fetch Parent Doc]
        RetrievalLogic -- No --> Chunk[Use Specific Chunk]
        
        Parent --> Assembler
        Chunk --> Assembler
        
        Assembler["**Context Assembler**<br>(Fuses Rewritten Query + Best Context)"] -->|Prompt| LLM[LLM Generation]
        LLM -->|Response| User
    end

    style Scraper fill:#e1f5fe,stroke:#01579b,color:black
    style Ingestion fill:#fff3e0,stroke:#e65100,color:black
    style Chatbot fill:#e8f5e9,stroke:#1b5e20,color:black
    
    %% Force black lines
    linkStyle default stroke:black,stroke-width:2px
```

### 🧠 Deep Dive: The "Context Assembler"
The **Context Assembler** is the intelligent fusion layer that brings these strategies together.
It takes:
1.  **The Rewritten Query** (Architecture 1): Ensures the question is precise.
2.  **The Best Available Context** (Architecture 2):
    *   If it's a simple product -> Retrieves specific **Chunks**.
    *   If it's a complex Bundle -> Retrieves the full **Parent Document**.

It then **Assembles** the final prompt: *"The user is asking about [Product A] (Rewritten). Here is the [Full Brochure/Specific Spec] (Context). Answer specifically about Pricing."*

---

## �️ System Components

1.  **Ingestion (`src/ingestion`)**:
    - Splits generic files into chunks.
    - specialized splitting for **Multi-Product Bundles** (Parent) -> Product-Specific Sections (Children).
2.  **Engine (`src/chatbot`)**:
    - **CombinedRewriter**: Manages state (Product/Intent) and rewrites queries.
    - **RAGEngine**: Orchestrates retrieval, using state to filter and fetch Parents.
3.  **Frontend Interface**:
    - Simple chat interface for demonstration.

## 📦 Repository Structure

This repository is a **Reference Implementation** of advanced RAG techniques.

```text
.
├── 📂 data/
│   └── synthetic_raw/       # Reference Dataset (Schema Only)
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
