import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.llm_client import LLMClient

class QuizAgent:
    """Agent responsible for generating practice quizzes and exercises."""
    
    def __init__(self):
        self.system_prompt = (
            "You are a Legendary Quiz Master AI.\n"
            "Do not include any 'Assistant:' or 'Agent:' prefixes.\n"
            "Your goal is to make learning fun and visually exciting!\n"
            "D) [option D]\n\n"
            "STRICT RULES:\n"
            "1. The '### 🎮 Challenge Accepted!' intro MUST be the first thing in your response.\n"
            "2. Each option (A, B, C, D) MUST be on its own NEW LINE.\n"
            "3. Do NOT provide the answer in the initial question."
        )

    def process(self, prompt: str, context: str = "") -> str:
        prompt_lower = prompt.lower().strip()
        
        # Assume they are answering unless they use keywords to request a brand new quiz
        is_answering = True
        if any(kw in prompt_lower for kw in ['quiz', 'test', 'exam', 'practice', 'generate', 'create', 'conduct']):
            is_answering = False
        
        if is_answering:
            full_prompt = (
                f"Previous Conversation:\n{context}\n\n"
                f"User has just submitted the answer: {prompt}\n\n"
                "INSTRUCTION:\n"
                "1. Look at the previous question in the history and identify the correct option.\n"
                "2. Tell the user if they were right or wrong enthusiastically.\n"
                "3. Explain why briefly.\n"
                "4. End by asking if they are ready for the next one.\n"
                "CRITICAL: Do NOT generate a new question yet. Do NOT pretend to be the user. Stop immediately after the follow-up question."
            )
        else:
            full_prompt = (
                f"Previous Conversation:\n{context}\n\n"
                f"User request: {prompt}\n\n"
                "INSTRUCTION:\n"
                "1. START with your '### 🎮 Challenge Accepted!' intro.\n"
                "2. Generate exactly one multiple-choice question on the requested topic.\n"
                "3. Use NEW LINES for every option."
            )
            
        # Generate raw response
        text = LLMClient.generate_response(full_prompt, self.system_prompt)
        
        # Hard Python-side filter to strictly enforce formatting ONLY when generating new questions
        if not is_answering:
            cutoffs = ["\nAnswer", "Correct answer", "Answer:", "\nCorrect", "The answer is", "\nOption"]
            for cutoff in cutoffs:
                if cutoff.lower() in text.lower():
                    # Case-insensitive split to chop off anything after the cutoff keyword
                    text = re.split(re.escape(cutoff), text, flags=re.IGNORECASE)[0]
                
        # Clean up any trailing whitespace after cutting
        return text.strip()
