class ConversationMemory:
    """
    Hand-crafted memory management.
    Manually manages the context window by sliding the history.
    """
    def __init__(self, max_tokens=1000):
        self.history = []  # List of {"role": "...", "content": "..."}
        self.max_tokens = max_tokens

    def add_interaction(self, user_msg: str, assistant_msg: str):
        """Add a turn to history."""
        self.history.append({"role": "user", "content": user_msg})
        self.history.append({"role": "assistant", "content": assistant_msg})
    
    def get_messages(self, system_prompt: str = None) -> list:
        """
        Get the messages list for the LLM, trimming older history if needed.
        (Simple approximation: 1 token ~= 4 chars)
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        
        # Calculate tokens roughly
        current_chars = len(system_prompt or "")
        
        # Take recent history that fits
        recent_history = []
        for msg in reversed(self.history):
            msg_len = len(msg['content'])
            if current_chars + msg_len > self.max_tokens * 4:
                break
            recent_history.insert(0, msg)
            current_chars += msg_len
            
        messages.extend(recent_history)
        return messages

    def clear(self):
        self.history = []
