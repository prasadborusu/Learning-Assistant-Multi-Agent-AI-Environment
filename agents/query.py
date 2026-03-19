from utils.llm_client import LLMClient

class QueryAgent:
    """Agent responsible for explaining concepts and answering theoretical learning questions."""
    
    def __init__(self):
        self.system_prompt = (
            "You are a High-Performance AI Learning Partner.\n"
            "Do not include any 'Assistant:' or 'Agent:' prefixes.\n"
            "If the user just says 'hi' or 'hello', give a vibrant, one-sentence greeting with an emoji. 👋\n"
            "If they ask a learning question, provide a structured 'Deep Dive' response:\n"
            "1. Start with a ### Brief Overview.\n"
            "2. Use 🧠 or 💡 emojis for key conceptual breakthroughs.\n"
            "3. Use bolding for technical terms.\n"
            "4. ALWAYS finish with a '### 🚀 Pro Tip' or 'Next Steps' suggestion to keep the learning momentum going."
        )

    def process(self, prompt: str, context: str = "") -> str:
        full_prompt = f"Conversation History:\n{context}\n\nUser: {prompt}"
        return LLMClient.generate_response(full_prompt, self.system_prompt)
