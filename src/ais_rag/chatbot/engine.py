import json
import re
from typing import List, Dict, Optional
from ..config import AVAILBLE_SPORTS, PACKAGE_TO_SPORT, K_CHUNKS, MAX_LLM_TOKENS
from ..ingestion.vector_store import VectorStore
from .memory import ConversationMemory
from .llm_client import LLMClient

# Check config spelling in file usage vs definition (AVAILABLE_SPORTS vs AVAILBLE...)
# I will fix the config import to match config.py definition
from ..config import AVAILABLE_SPORTS

class RAGEngine:
    def __init__(self):
        self.vector_store = VectorStore()
        self.collection = self.vector_store.get_collection()
        self.llm = LLMClient()
        self.memory = ConversationMemory()
        self.model = self.vector_store.embedding_fn # Re-use embedding function
        
        # State
        self.selected_sport = None
        self.last_chunks = []
        
        # Load Parents Cache (Need to ensure these are generated)
        # For this refactor, we query parents dynamically or need a way to fetch them.
        # The ingestion logic suggests parents are just NOT in vector DB as "embeddings" but as text?
        # NO, wait. Hierarchy logic created parent DOCS. But did we add them to Chroma in Ingestion?
        # In `hierarchy.py`, we returned `parent_doc`.
        # In the `chunks` list, we only added children?
        # In the original notebook, Parents were created in a dict `parents`.
        # We need to simulate that `parents` lookup.
        # I will modify `retrieve_chunks_for_sport` to fetch Parent content from vector DB?
        # Or I'll assume parents are also indexed but we need to ID them.
        # Let's check `ingestion` strategy again.
        # If I want to implement the "Fetch Full Parent" logic, I need access to the full parent content.
        # I will make sure the Parent Content is stored in ChromaDB or a file.
        # For simplicity in this `engine.py`, I will assume I can query the parent ID from Chroma if present,
        # OR I should have saved them. 
        # Since I can't easily persist a JSON side-file without `ingestion` running first,
        # I will implement a "Lazy Load" or assume they are in Chroma with type='parent'.
        pass

    def retrieve_chunks_for_sport(self, query: str, sport: str, k: int = 5):
        try:
            query_embedding = self.model(texts=[query])[0] # Chroma embed fn expects list
            
            n_retrieve = k * 3
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=n_retrieve
            )
            
            if not results['documents'] or not results['documents'][0]:
                return []
            
            chunks = results['documents'][0]
            metadatas = results['metadatas'][0]
            distances = results['distances'][0]
            
            filtered = []
            seen_parents = set()
            
            for chunk, meta, dist in zip(chunks, metadatas, distances):
                # Filter by sport logic
                chunk_sports = meta.get('sport', '')
                sport_list = [s.strip() for s in chunk_sports.split(',')]
                
                if sport and sport not in sport_list:
                    continue
                
                similarity = 1 - dist
                is_multi = str(meta.get('is_multi_sport')).lower() == 'true'
                parent_id = meta.get('parent_id')
                
                if is_multi and parent_id:
                    if parent_id in seen_parents:
                        continue
                    
                    # RETRIEVE PARENT CONTENT
                    # In this design, we try to fetch the parent doc from the collection itself 
                    # if we indexed it?
                    # If we didn't index the parent itself (embeddings), we can't query it easily by ID 
                    # unless we use `collection.get(ids=[parent_id])`.
                    
                    parent_res = self.collection.get(ids=[parent_id])
                    if parent_res['documents']:
                        full_content = parent_res['documents'][0]
                        filtered.append({
                            "content": full_content,
                            "type": "parent",
                            "sport": chunk_sports,
                            "package": meta.get('package'),
                            "similarity": similarity + 0.05 # Boost parents
                        })
                        seen_parents.add(parent_id)
                else:
                    filtered.append({
                        "content": chunk,
                        "type": "chunk",
                        "sport": chunk_sports,
                        "package": meta.get('source_file'),
                        "similarity": similarity
                    })
                
                if len(filtered) >= k:
                    break
            
            return filtered
            
        except Exception as e:
            print(f"Retrieval Error: {e}")
            return []

    def detect_intent(self, query: str):
        # ... (Implement the detection prompt logic from original notebook) ...
        # Simplified for brevity in this artifact
        pass

    def chat(self, user_query: str):
        # 1. Detect Intent/Sport
        # ...
        
        # 2. Retrieve
        chunks = self.retrieve_chunks_for_sport(user_query, self.selected_sport, k=K_CHUNKS)
        self.last_chunks = chunks
        
        # 3. Build Context
        context = ""
        for i, c in enumerate(chunks, 1):
             context += f"\n[Document {i}] ({c['type']})\n{c['content']}\n"
        
        # 4. System Prompt
        system_prompt = f"""You are "Nong Gila" (น้องกีฬา), AIS Sports Assistant.
Answer based on context:
{context}
"""
        # 5. Call LLM with Memory
        messages = self.memory.get_messages(system_prompt)
        messages.append({"role": "user", "content": user_query})
        
        response = self.llm.generate(messages)
        
        # 6. Update Memory
        self.memory.add_interaction(user_query, response)
        
        return response

    def set_sport(self, sport: str):
        self.selected_sport = sport
