import pytest
from ais_rag.chatbot.memory import ConversationMemory

def test_memory_window():
    """Test that memory slides correctly."""
    mem = ConversationMemory(max_tokens=20)
    
    # Add dummy long interactions
    mem.add_interaction("User says hi", "AI says hello back")
    mem.add_interaction("User asks question", "AI answers detailed response")
    
    messages = mem.get_messages(system_prompt="System")
    
    # Ensure it didn't keep infinite history
    assert len(messages) <= 5 # System + 2 turns (max)
    assert messages[0]['role'] == 'system'

def test_chunking_config():
    """Test standard chunk sizes."""
    from ais_rag.config import K_CHUNKS
    assert K_CHUNKS > 0
