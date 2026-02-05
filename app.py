import sys
import os
import gradio as gr

# Ensure src is in path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from ais_rag.chatbot.engine import RAGEngine
from ais_rag.config import AVAILABLE_SPORTS

# Initialize Engine
print("🚀 Initializing AIS Sport RAG Engine...")
engine = RAGEngine()
print("✅ Engine Ready!")

def respond(message, history):
    # History handling is done inside RAGEngine's memory for context,
    # but Gradio passes history for display.
    # We update the memory with the latest turn after generation.
    return engine.chat(message)

def set_sport(sport_key):
    engine.set_sport(sport_key)
    if sport_key:
        return f"🔒 Selected: {AVAILABLE_SPORTS[sport_key]}"
    return "🌐 All Sports"

with gr.Blocks(title="AIS Sport RAG") as demo:
    gr.Markdown("# 🏆 AIS Sport Expert Chatbot\nAsk about EPL, NBA, NFL, Golf, Tennis packages!")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🔒 Lock Sport Context")
            for key, name in AVAILABLE_SPORTS.items():
                gr.Button(name).click(
                    fn=lambda k=key: set_sport(k), 
                    outputs=[gr.Label(label="Current Context")]
                )
            gr.Button("🌐 All Sports").click(
                fn=lambda: set_sport(None),
                outputs=[gr.Label(label="Current Context")]
            )
            
        with gr.Column(scale=4):
            chatbot = gr.ChatInterface(
                respond,
                type="messages",
                title="Conversation",
                description="Ask me about packages, prices, and channels.",
            )

if __name__ == "__main__":
    demo.launch(share=False)
