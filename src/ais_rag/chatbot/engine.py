import json
from typing import List, Dict, Optional
from ..config import AVAILABLE_SPORTS, PROCESSED_DATA_DIR, K_CHUNKS, MAX_LLM_TOKENS
from ..ingestion.vector_store import VectorStore
from .memory import ConversationMemory
from .llm_client import LLMClient
from .rewriter import CombinedRewriter

class RAGEngine:
    def __init__(self):
        self.vector_store = VectorStore()
        self.collection = self.vector_store.get_collection()
        self.llm = LLMClient()
        self.memory = ConversationMemory()
        self.model = self.vector_store.embedding_fn
        
        # V3 Logic: Combined Rewriter
        self.rewriter = CombinedRewriter(self.llm)
        
        # State Management (Sticky Context)
        self.active_sport = None
        self.active_intent = None
        
        # Load Parents Cache
        self.parents = {}
        parents_path = PROCESSED_DATA_DIR / "parents.json"
        if parents_path.exists():
            try:
                with open(parents_path, 'r', encoding='utf-8') as f:
                    self.parents = json.load(f)
                print(f"✅ Loaded {len(self.parents)} parent documents from cache.")
            except Exception as e:
                print(f"⚠️ Failed to load parents.json: {e}")
        else:
            print("⚠️ parents.json not found. Hierarchy retrieval will not work.")

    def retrieve_chunks_for_sport(self, query: str, sport: str, k: int = 5):
        try:
            # Generate embedding
            if hasattr(self.model, 'encode'):
                 query_embedding = self.model.encode(query).tolist()
            else:
                 query_embedding = self.model([query])[0]
            
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
                chunk_sports = meta.get('sport', '')
                sport_list = [s.strip() for s in chunk_sports.split(',')]
                
                # Filter by sport if specified
                # V3 Logic: If sport is locked, strictly filter
                if sport and sport != "MULTI":
                    if sport not in sport_list and "MULTI" not in sport_list: 
                        # Allow MULTI content (like Ultimate package) even if looking for specific sport
                        if not (sport == "GOLF" and ("GOLF1" in sport_list or "GOLF2" in sport_list)): # Special case
                             continue
                
                similarity = 1 - dist
                is_multi = str(meta.get('is_multi_sport')).lower() == 'true'
                parent_id = meta.get('parent_id')
                
                # === Parent-Child Logic ===
                if is_multi and parent_id:
                    if parent_id in seen_parents:
                        continue
                    
                    if parent_id in self.parents:
                        parent_doc = self.parents[parent_id]
                        filtered.append({
                            "content": parent_doc['full_content'], # FULL TEXT
                            "type": "parent",
                            "sport": chunk_sports,
                            "package": parent_doc.get('package', 'Unknown'),
                            "similarity": similarity + 0.1 # Boost parents
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
            import traceback
            traceback.print_exc()
            return []

    def chat(self, user_query: str):
        print(f"\n💬 User: {user_query}")
        
        # 1. Combined Analysis (V3)
        analysis = self.rewriter.analyze_and_rewrite(
            query=user_query,
            history=self.memory.history,
            active_sport=self.active_sport,
            active_intent=self.active_intent
        )
        
        rewritten_query = analysis.get('rewritten_query', user_query)
        detected_sport = analysis.get('sport')
        detected_intent = analysis.get('intent')
        
        print(f"🕵️ Analysis: Sport={detected_sport}, Intent={detected_intent}")
        print(f"🔄 Rewritten: {rewritten_query}")

        # 2. Update State (Sticky logic)
        if detected_sport and detected_sport != 'None':
            self.active_sport = detected_sport
        
        if detected_intent and detected_intent != 'None':
            self.active_intent = detected_intent
            
        print(f"📌 Current State -> Sport: {self.active_sport}, Intent: {self.active_intent}")

        # 3. Retrieve
        chunks = self.retrieve_chunks_for_sport(rewritten_query, self.active_sport, k=K_CHUNKS)
        
        # 4. Build Context
        context = ""
        for i, c in enumerate(chunks, 1):
             type_label = "📄 FULL PARENT" if c['type'] == 'parent' else "🧩 CHUNK"
             context += f"\n[Doc {i}] {type_label} (Sport: {c['sport']})\n{c['content']}\n"
        
        if not context:
            # If no context found with lock, maybe try without lock or fallback? 
            # For now, strict as per user request.
            context = "ไม่พบข้อมูลที่เกี่ยวข้องในฐานข้อมูล"

        # 5. System Prompt (V3 Style)
        sport_info = f"Active Sport: {self.active_sport}" if self.active_sport else "Active Sport: None (General)"
        
        system_prompt = f"""คุณคือ 'น้องกีฬา' ผู้ช่วย AIS ที่เป็นมิตร (v3 Logic)
สถานะปัจจุบัน: {sport_info}
หัวข้อที่คุยอยู่: {self.active_intent}

CONTEXT:
{context}

คำแนะนำ:
1. ตอบโดยใช้ข้อมูลใน CONTEXT เท่านั้น
2. ถ้าผู้ใช้ถามเรื่องราคา/แพ็กเกจ และเรามี Active Sport ให้เน้นแพ็กเกจของกีฬานั้น
3. สำหรับ PLAY ULTIMATE: ต้องบอกเสมอว่ามีครบทั้ง 5 กีฬา + Streaming Services (Netflix, Disney+, etc.)
4. ตอบสั้นกระชับ เป็นธรรมชาติ (ภาษาไทย)
"""
        
        # 6. Call LLM
        messages = [{"role": "system", "content": system_prompt}]
        # Add recent history for flow
        for turn in self.memory.history[-2:]:
             messages.append(turn)
        messages.append({"role": "user", "content": rewritten_query}) # Feed rewritten query to LLM for clarity? Or original? V3 uses rewritten in prompt.
        
        response = self.llm.generate(messages)
        
        # 7. Update Memory
        self.memory.add_interaction(user_query, response)
        
        return response

    def set_sport(self, sport: str):
        # Manually force state
        self.active_sport = sport

