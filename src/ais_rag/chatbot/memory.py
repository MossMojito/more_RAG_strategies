from typing import List, Dict, Any

class ConversationMemory:
    """
    Memory with Summarization capabilities.
    Maintains:
    1. Current Summary (Long-term)
    2. Recent History (Short-term)
    """
    def __init__(self, max_tokens=2000):
        self.history = []  # List of {"role": "...", "content": "..."}
        self.summary = ""
        self.max_tokens = max_tokens

    def add_interaction(self, user_msg: str, assistant_msg: str):
        """Add a turn to history."""
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})

    def get_messages(self, system_prompt: str = None) -> list:
        """
        Get messages including System + Summary + Recent History.
        """
        messages = []
        
        # 1. System Prompt + Summary
        full_system_content = system_prompt or ""
        if self.summary:
            full_system_content += f"\n\nPREVIOUS CONVERSATION SUMMARY:\n{self.summary}"
            
        if full_system_content:
            messages.append({"role": "system", "content": full_system_content})

        # 2. Recent History
        # Simple pruning based on estimated token count (1 token ~ 4 chars)
        current_chars = len(full_system_content)
        recent_history = []
        
        for msg in reversed(self.history):
            msg_len = len(msg['content'])
            if current_chars + msg_len > self.max_tokens * 4:
                break
            recent_history.insert(0, msg)
            current_chars += msg_len
            
        messages.extend(recent_history)
        return messages

    def summarize(self, llm_client):
        """
        Compact existing history into self.summary
        """
        if len(self.history) < 3:
            return # No need to summarize yet
            
        # Keep last 2 turns, summarize the rest
        to_summarize = self.history[:-2]
        self.history = self.history[-2:]
        
        conversation_text = ""
        for msg in to_summarize:
            role = "User" if msg['role'] == 'user' else "AI"
            conversation_text += f"{role}: {msg['content']}\n"
            
        prompt = f"""Summarize the following conversation in Thai. Keep key details about packages, sports, or user preferences.
        
Current Summary: {self.summary}

New Conversation:
{conversation_text}

New Summary:"""

        try:
             # This is a synchronous call to LLM
             response = llm_client.generate([{"role": "user", "content": prompt}])
             self.summary = response.strip()
             print(f"🧠 Memory Summarized: {self.summary[:50]}...")
        except Exception as e:
            print(f"⚠️ Summarization failed: {e}")
            # Restore history if failed? Or just keep it loosely
            self.history = to_summarize + self.history

    def clear(self):
        self.history = []
        self.summary = ""
