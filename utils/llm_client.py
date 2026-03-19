import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("HUGGINGFACE_API_KEY")
client = InferenceClient(token=API_KEY) if API_KEY else None

if not API_KEY:
    print("WARNING: HUGGINGFACE_API_KEY is not set in environment or .env file.")

# Using widely available, robust instruction models on HuggingFace Free Tier
classification_model = "HuggingFaceH4/zephyr-7b-beta"
generation_model = "HuggingFaceH4/zephyr-7b-beta" 

class LLMClient:
    """Wrapper for all Generative AI calls using Hugging Face Inference API."""
    
    @staticmethod
    def generate_response(prompt: str, system_instruction: str = None, fast: bool = False) -> str:
        """
        Generate a text response based on a prompt and optional system instructions.
        """
        if not client:
            return "Error: HUGGINGFACE_API_KEY is missing. Please add it to .env"

        model_to_use = classification_model if fast else generation_model
        
        try:
            messages = []
            if system_instruction:
                messages.append({"role": "system", "content": system_instruction})
            
            messages.append({"role": "user", "content": prompt})
                
            response = client.chat_completion(
                model=model_to_use,
                messages=messages,
                temperature=0.7 if not fast else 0.3,
                max_tokens=1000
            )
            
            text = response.choices[0].message.content
            # Bulletproof fix against 7B model conversational hallucinations
            stop_words = [
                "\nUser:", "\nuser:", "User Response:", "User:", "<|user|>", 
                "\nAssistant:", "\nassistant:", "User answered:", "\nQuestion:"
            ]
            for word in stop_words:
                if word in text:
                    text = text.split(word)[0].strip()
            
            return text
        except Exception as e:
            return f"Error communicating with HuggingFace service: {str(e)}"
