from typing import List, Dict

class MemoryManager:
    """Manages short-term conversation history for multiple sessions."""
    
    def __init__(self):
        # A simple in-memory store: { session_id: [ {"role": "user"/"agent", "content": "..."} ] }
        self.sessions: Dict[str, List[Dict[str, str]]] = {}

    def add_message(self, session_id: str, role: str, content: str):
        """Append a message to the session's history."""
        if session_id not in self.sessions:
            self.sessions[session_id] = []
            
        self.sessions[session_id].append({"role": role, "content": content})
        
        # Keep only the last 10 messages to prevent context overflow
        if len(self.sessions[session_id]) > 20: 
            self.sessions[session_id] = self.sessions[session_id][-20:]

    def get_history(self, session_id: str) -> str:
        """Retrieve conversation history formatted as a string for LLM context."""
        if session_id not in self.sessions:
            return "No previous conversation context."
            
        history = self.sessions[session_id]
        if not history:
            return "No previous conversation context."
            
        formatted_history = "Conversation History:\n"
        for msg in history:
            role_name = "User" if msg["role"] == "user" else "Agent"
            formatted_history += f"{role_name}: {msg['content']}\n"
            
        return formatted_history
