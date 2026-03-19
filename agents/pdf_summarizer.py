import sys
import os
from pypdf import PdfReader
from utils.llm_client import LLMClient

class PDFSummarizerAgent:
    """Agent responsible for extracting text from PDF and generating summaries."""
    
    def __init__(self):
        self.system_prompt = (
            "You are an expert Document Analyst AI.\n"
            "Do not include any 'Assistant:' or 'Agent:' prefixes in your response.\n"
            "Your task is to take the raw text extracted from a PDF and provide a clear, concise executive summary.\n"
            "Use bullet points for key takeaways and keep the overall summary under 200 words.\n"
            "If the text appears corrupted or empty, politely inform the user."
        )

    def process_pdf(self, file_path: str) -> str:
        """Extracts text from PDF and returns an AI-generated summary."""
        try:
            reader = PdfReader(file_path)
            full_text = ""
            
            # Extract text from first 5 pages to stay within token limits
            num_pages = min(len(reader.pages), 5)
            for i in range(num_pages):
                page = reader.pages[i]
                full_text += page.extract_text() + "\n"
                
            if not full_text.strip():
                return "I couldn't find any readable text in that PDF. It might be a scanned image or protected."

            num_pages_total = len(reader.pages)
            prompt = (
                f"Below is text extracted from the first {num_pages} pages of a {num_pages_total}-page PDF document.\n"
                f"Please provide a high-level summary of its contents.\n\n"
                f"TEXT:\n{full_text[:4000]}" # Truncate to avoid context overflow
            )
            
            return LLMClient.generate_response(prompt, self.system_prompt)
            
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
