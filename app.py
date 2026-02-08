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
    # Manual override for V3 logic
    engine.set_sport(sport_key)
    if sport_key:
        return f"🔒 Manually Locked: {AVAILABLE_SPORTS[sport_key]}"
    return "🌐 Auto-Detect Mode"

with gr.Blocks(title="AIS Sport RAG (V3)") as demo:
    gr.Markdown("# 🏆 AIS Sport Expert (V3 Logic)\n**Core Strategy**: Combined Analysis + Hierarchical Retrieval\n**Dataset**: Minimal (NBA + Ultimate Only)")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("### 🔒 Manual Override")
            gr.Markdown("The AI automatically detects sport, but you can force it here:")
            
            # Dynamic buttons from config
            for key, name in AVAILABLE_SPORTS.items():
                gr.Button(name).click(
                    fn=lambda k=key: set_sport(k), 
                    outputs=[gr.Label(label="Current State")]
                )
            
            gr.Button("🌐 Auto-Detect (Reset)").click(
                fn=lambda: set_sport(None),
                outputs=[gr.Label(label="Current State")]
            )
            
        with gr.Column(scale=4):
            chatbot = gr.ChatInterface(
                respond,
                title="Conversation",
                description="Ask me about packages, prices, and channels.",
            )

if __name__ == "__main__":
    demo.launch(share=False)
