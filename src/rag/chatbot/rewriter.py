import json
from typing import List, Dict, Optional
from .llm_client import LLMClient

class CombinedRewriter:
    """
    V3 Logic: Merged Analysis & Rewrite.
    Handles Sport/Intent detection and Query Rewriting in ONE efficient LLM call.
    """
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client

    def analyze_and_rewrite(self, query: str, history: List[Dict], active_sport: Optional[str] = None, active_intent: Optional[str] = None) -> Dict:
        """
        Corresponds to `analyze_and_rewrite_combined` in the notebook.
        """
        # Get last user message for context
        last_user_msg = "None"
        if history:
            # history is list of dicts: [{'role': 'user', 'content': '...'}, ...]
            # Find last user message
            for msg in reversed(history):
                if msg['role'] == 'user':
                    last_user_msg = msg['content']
                    break
        
        context_summary = f"""
บริบทปัจจุบัน:
- Sport Lock: {active_sport or 'None'}
- Topic Lock: {active_intent or 'None'}
- Last Message: {last_user_msg}
"""
        
        combined_prompt = f"""คุณคือระบบวิเคราะห์และเขียนคำถามใหม่ (Rewriter & Analyzer)

{context_summary}

คำถามปัจจุบัน: "{query}"

งานของคุณ:
1. rewritten_query: เขียนคำถามใหม่ให้เป็น Standalone Query ที่สมบูรณ์ (เช่น 'ขอโปรโมชั่นของ NBA' แทนที่จะเป็น 'ของ NBA')
2. sport: ระบุกีฬา (EPL, NBA, NFL, TENNIS, GOLF, MULTI, หรือ None)
3. intent: ระบุหัวข้อ/Topic สั้นๆ (เช่น 'pricing', 'support', 'promo') **ห้ามยึดติดหัวข้อเดิมหากเปลี่ยนเรื่อง**
4. is_followup: true/false เมื่อเป็นคำถามต่อเนื่องสั้นๆ

ตอบเป็น JSON เท่านั้น:
{{
  "rewritten_query": "...",
  "sport": "...",
  "intent": "...",
  "is_followup": true|false
}}"""
        
        try:
            # We use a simple one-shot call
            response = self.llm.generate([
                {"role": "user", "content": combined_prompt}
            ])
            
            # Clean response to ensure JSON
            response = response.strip()
            if "```json" in response:
                response = response.split("```json")[1].split("```")[0].strip()
            elif "```" in response:
                response = response.split("```")[1].split("```")[0].strip()

            result = json.loads(response)
            return result
        except Exception as e:
            print(f"⚠️ Combined Rewriter Error: {e}")
            # Fallback
            return {
                "rewritten_query": query, 
                "sport": active_sport, 
                "intent": active_intent,
                "is_followup": False
            }

