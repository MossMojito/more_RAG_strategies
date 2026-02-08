import json
import re
from typing import Dict, List, Optional
from ..config import AVAILABLE_SPORTS, PACKAGE_TO_SPORT, SPORT_NAMES
from .llm_client import LLMClient

class Router:
    def __init__(self, llm_client: LLMClient):
        self.llm = llm_client
        self.selected_sport: Optional[str] = None
        self.conversation_sports: List[str] = []

    def set_sport_filter(self, sport: Optional[str]):
        """Manually lock the sport context."""
        self.selected_sport = sport
        print(f"🔒 Manual Sport Lock: {sport}")

    def detect_intent(self, query: str) -> Dict:
        """
        Use LLM to detect sports and intent from the query.
        """
        sports_list = ", ".join(AVAILABLE_SPORTS.keys())
        
        prompt = f"""วิเคราะห์คำถามและตอบเป็น JSON:

กีฬาที่มีในระบบ: {sports_list}
ชื่อแพ็กเกจที่อาจพบ:
- MONOMAX = EPL
- GOLF1, GOLF2 = GOLFPL
- PLAY SPORTS, PLAY ULTIMATE = MULTI (รวมหลายกีฬา)

คำถาม: "{query}"

ตอบเป็น JSON เท่านั้น (ไม่ต้องมี markdown `json`):
{{
  "detected_sports": ["CODE_OF_SPORT"],
  "is_asking_about_package": true/false,
  "package_name": "ชื่อแพ็กเกจถ้ามี หรือ null",
  "intent": "สรุปเจตนาสั้นๆ"
}}"""

        try:
            response = self.llm.generate([
                {"role": "user", "content": prompt}
            ], max_tokens=300)
            
            # Clean generic markdown
            clean = re.sub(r'```json|```', '', response).strip()
            analysis = json.loads(clean)
            return analysis
        except Exception as e:
            print(f"⚠️ Router detection failed: {e}")
            # Fallback: Keyword matching
            found = []
            q_upper = query.upper()
            for code, keywords in SPORT_NAMES.items():
                if any(k in q_upper for k in keywords):
                    found.append(code)
            
            return {
                "detected_sports": found,
                "is_asking_about_package": False,
                "package_name": None,
                "intent": query
            }

    def get_search_filters(self, analysis: Dict) -> List[Optional[str]]:
        """
        Determine which sports to search based on Lock + Detection.
        Returns a list of sport codes (or [None] for all).
        """
        detected = analysis.get("detected_sports", [])
        
        # 1. If Locked, strict search on lock
        if self.selected_sport:
            return [self.selected_sport]
        
        # 2. If Detected, search those
        if detected:
            return detected
            
        # 3. Else search all
        return [None]
