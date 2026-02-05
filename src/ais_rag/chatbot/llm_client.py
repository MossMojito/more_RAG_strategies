import os
from openai import OpenAI

class LLMClient:
    def __init__(self, api_key=None, base_url=None, model_name="databricks-claude-sonnet-4-5"):
        self.api_key = api_key or os.getenv("DATABRICKS_TOKEN")
        self.base_url = base_url or os.getenv("DATABRICKS_ENDPOINT")
        self.model_name = model_name
        
        if not self.api_key:
            print("⚠️ WARNING: DATABRICKS_TOKEN not set.")
            
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
