from utils.llm_client import LLMClient

class RecommendationAgent:
    """Agent responsible for suggesting external resources, books, and courses."""
    
    def __init__(self):
        self.system_prompt = (
            "You are an expert Resource Recommender AI.\n"
            "Do not include any 'Assistant:' or 'Agent:' prefixes in your response.\n"
            "Directly list exactly 2 highly relevant books, links, or articles based on the user's topic.\n"
            "CRITICAL: Keep it brief, and ALWAYS end your response by asking a conversational follow-up question (e.g., 'Have you read either of these?' or 'Should I find some YouTube videos instead?')."
        )

    def process(self, prompt: str, context: str = "") -> str:
        """Process the user's resource request."""
        full_prompt = f"Conversation History:\n{context}\n\nUser: {prompt}"
        return LLMClient.generate_response(
            prompt=full_prompt,
            system_instruction=self.system_prompt,
            fast=False
        )
