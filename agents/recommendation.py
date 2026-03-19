from utils.llm_client import LLMClient

class RecommendationAgent:
    """Agent responsible for suggesting external resources, books, and courses."""
    
    def __init__(self):
        self.system_prompt = (
            "You are a Platinum Resource Specialist AI.\n"
            "Do not include any 'Assistant:' or 'Agent:' prefixes.\n"
            "Provide high-value learning recommendations structured as follows:\n"
            "1. ### 🎯 Recommended Resources\n"
            "2. Use 📚 for books, 💻 for courses, and 🔗 for websites.\n"
            "3. For each resource, provide a 1-sentence 'Why it's good' explanation.\n"
            "4. ALWAYS finish with a conversational question (e.g., 'Would you like a more beginner-friendly list?') to keep the user engaged."
        )

    def process(self, prompt: str, context: str = "") -> str:
        """Process the user's resource request."""
        full_prompt = f"Conversation History:\n{context}\n\nUser: {prompt}"
        return LLMClient.generate_response(
            prompt=full_prompt,
            system_instruction=self.system_prompt,
            fast=False
        )
