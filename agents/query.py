from utils.llm_client import LLMClient

class QueryAgent:
    """Agent responsible for explaining concepts and answering theoretical learning questions."""
    
    def __init__(self):
        self.system_prompt = (
            "You are a casual AI Learning Assistant.\n"
            "Do not include any 'Assistant:' or 'Agent:' prefixes in your response.\n"
            "If the user just says 'hi', 'hello', or 'how are you', reply with exactly one short sentence (e.g. 'Hey! 👋 What's up?'). Do not bombard them with questions.\n"
            "If they ask a learning question, explain it clearly and briefly in 2 sentences max.\n"
            "Only ask a follow-up question at the end if you actually just explained a concept."
        )

    def process(self, prompt: str, context: str = "") -> str:
        full_prompt = f"Conversation History:\n{context}\n\nUser: {prompt}"
        return LLMClient.generate_response(full_prompt, self.system_prompt)
