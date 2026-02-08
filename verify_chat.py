import sys
import os

# Add src to path
sys.path.append(os.path.abspath("src"))

from ais_rag.chatbot.engine import RAGEngine

def test_chat():
    print("🚀 Initializing Chatbot Engine...")
    try:
        engine = RAGEngine()
    except Exception as e:
        print(f"❌ Failed to initialize engine: {e}")
        return

    test_queries = [
        "Play Ultimate ราคาเท่าไหร่",
        "แล้วมีอะไรให้ดูบ้าง", # Tests Memory & Rewriting ("What does [Play Ultimate] have?")
        "อยากดู NBA ต้องสมัครแพ็กไหน", # Tests Router (NBA intent)
        "ราคาของแพ็กเกจนั้นเท่าไหร่", # Tests Rewriting ("How much is [NBA] package?")
    ]

    print("\n💬 Starting Conversation Test...")
    for query in test_queries:
        print("-" * 50)
        print(f"🗣️ User: {query}")
        try:
            response = engine.chat(query)
            print(f"🤖 Bot: {response}")
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_chat()
