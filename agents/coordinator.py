import re
from agents.query import QueryAgent
from agents.recommendation import RecommendationAgent
from agents.quiz import QuizAgent
from agents.pdf_summarizer import PDFSummarizerAgent

class CoordinatorAgent:
    """The central brain that decides which agent should handle the user's request."""
    
    def __init__(self):
        self.query_agent = QueryAgent()
        self.recommendation_agent = RecommendationAgent()
        self.quiz_agent = QuizAgent()
        self.pdf_agent = PDFSummarizerAgent()
        
    def classify_intent(self, text: str, context: str = "") -> str:
        """
        A heuristic router that leverages context to lock into active agent sessions.
        """
        text = text.lower().strip()
        
        # PDF/Document summarization detection
        if any(kw in text for kw in ['pdf', 'summarize', 'document', 'read this', 'file']):
            return "PDF"
        
        # If the most recent conversation was a quiz question, lock the intent to QUIZ
        if context and ("A)" in context[-200:] or "Ready for the next one" in context[-200:] or "Question:" in context[-200:]):
            return "QUIZ"
        
        # Exact match heuristics
        if text in ['a', 'b', 'c', 'd', 'a)', 'b)', 'c)', 'd)', 'yes', 'yeah', 'yep', 'ready', 'sure', 'ok', 'okay', 'next']:
            return "QUIZ"
            
        quiz_keywords = ['quiz', 'test', 'exam', 'practice', 'exercise', 'question me']
        resource_keywords = ['resource', 'book', 'course', 'video', 'recommend', 'where to learn', 'link']
        
        if any(keyword in text for keyword in quiz_keywords):
            return "QUIZ"
        elif any(keyword in text for keyword in resource_keywords):
            return "RECOMMENDATION"
        else:
            # Default to conceptual query explanation
            return "QUERY"

    def process_request(self, prompt: str, context: str = "") -> dict:
        """
        Receives user input, makes a routing decision, executes the sub-agent,
        and returns a structured response.
        """
        intent = self.classify_intent(prompt, context)
        
        if intent == "QUIZ":
            selected_agent = "Quiz Master Agent"
            response = self.quiz_agent.process(prompt, context)
        elif intent == "RECOMMENDATION":
            selected_agent = "Resource Recommender Agent"
            response = self.recommendation_agent.process(prompt, context)
        elif intent == "PDF":
            selected_agent = "PDF Summarizer Agent"
            response = "I see you want to analyze a document! 📑 Please use the **Attachment** icon next to the chat box to upload your PDF, and I'll summarize it for you immediately."
        else:
            selected_agent = "General Query Agent"
            response = self.query_agent.process(prompt, context)
            
        return {
            "decision": selected_agent,
            "response": response,
            "intent": intent
        }
