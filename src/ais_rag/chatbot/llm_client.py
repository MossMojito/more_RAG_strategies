import os
from openai import OpenAI

class LLMClient:
    def __init__(self, api_key=None, base_url=None, model_name=None):
        # 1. Try Standard OpenAI / Compatible API first
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL") # Generic Base URL support
        self.model_name = model_name or os.getenv("MODEL_NAME", "gpt-4o")

        if not self.api_key:
            print("⚠️ WARNING: No API Key found (OPENAI_API_KEY). LLM calls will fail.")
            
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )

    def generate(self, messages: list, max_tokens: int = 3000, temperature: float = 0.3):
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                timeout=60
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"❌ LLM Error: {e}")
            return f"ขออภัยค่ะ ระบบขัดข้อง: {str(e)}"
