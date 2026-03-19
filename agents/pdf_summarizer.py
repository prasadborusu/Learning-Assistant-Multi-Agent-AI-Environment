import sys
import os
from pypdf import PdfReader
from utils.llm_client import LLMClient

class PDFSummarizerAgent:
    """Agent responsible for extracting text from PDF and generating summaries."""
    
    def __init__(self):
        self.system_prompt = (
            "You are a Precision Document Analyst AI.\n"
            "Do not include any 'Assistant:' or 'Agent:' prefixes.\n"
            "Your highest priority is ACCURATE EXTRACTION of metadata (Names, Dates, ID numbers).\n\n"
            "STRICT FORMATTING RULES:\n"
            "1. NAMES: Multi-line detection is CRITICAL. The user's name is 'Borusu Venkata Durga Prasad'. If you see it split, use the full name. Never truncate it to 'Borusa Durga' or 'Borusu Venkata Prasad'.\n"
            "2. Use a clear ### header for the main topic.\n"
            "3. Use 📑 and 💡 emojis for key findings.\n"
            "4. Provide 3-5 high-impact bullet points.\n"
            "5. ALWAYS include '### 🚀 Strategic Usage (PPT Suggestions)' with slide title ideas.\n"
            "6. Precision over summarization: Copy all titles, institutions, and names verbatim."
        )

    def process_pdf(self, file_path: str) -> str:
        """Extracts text from PDF and returns an AI-generated summary."""
        try:
            reader = PdfReader(file_path)
            full_text = ""
            
            import re
            
            # Extract text from more pages to ensure no certificates are missed
            num_pages = min(len(reader.pages), 10)
            for i in range(num_pages):
                page = reader.pages[i]
                full_text += page.extract_text() + "\n"
            
            # Robust Case-Insensitive Regex to join the split name found in user certificates
            full_text = re.sub(r'BORUSU\s+VENKATA\s+DURGA\s*\n\s*PRASAD', 'BORUSU VENKATA DURGA PRASAD', full_text, flags=re.IGNORECASE)
            full_text = re.sub(r'BORUSU\s+VENKATA\s*\n\s*DURGA\s*\n\s*PRASAD', 'BORUSU VENKATA DURGA PRASAD', full_text, flags=re.IGNORECASE)
                
            if not full_text.strip():
                return "I couldn't find any readable text in that PDF. It might be a scanned image or protected."

            num_pages_total = len(reader.pages)
            # Truncate text to stay within fast context limits of free-tier models
            # 6000 characters is usually more than enough for 10 pages of metadata
            processed_text = full_text[:6000]
            
            prompt = (
                f"Below is text extracted from a {num_pages_total}-page PDF document.\n\n"
                f"SOURCE TEXT (Partial):\n---\n{processed_text}\n---\n\n"
                "TASK:\n"
                "1. Identify the user: Borusu Venkata Durga Prasad.\n"
                "2. Provide a PREMIUM EXECUTIVE SUMMARY with the following components:\n"
                "   - A clear ### Header with the document title.\n"
                "   - Use 📑 for key certificate details.\n"
                "   - Use 💡 for skill highlights.\n"
                "   - 3-5 high-impact bullet points.\n"
                "   - A final '### 🚀 Strategic Usage (PPT Suggestions)' section.\n"
                "3. STICK TO THE FORMAT. No plain text blocks. High visual polish is mandatory."
            )
            
            from utils.llm_client import LLMClient
            response = LLMClient.generate_response(prompt, self.system_prompt)
            
            # Final Hammer Correction: Ensure the name is 100% accurate without doubling
            full_name = "Borusu Venkata Durga Prasad"
            # Replace common variations, ensuring we don't double up
            if "Borusu" in response or "Borusa" in response:
                # Remove any existing (potentially broken) name variations first
                response = response.replace("Borusu Venkata Durga Prasad", "___TEMP_NAME___")
                response = response.replace("Borusu Venkata Prasad", "___TEMP_NAME___")
                response = response.replace("Borusa Durga", "___TEMP_NAME___")
                response = response.replace("Borusu Venkata Durga", "___TEMP_NAME___")
                # Replace the placeholder with the perfect name
                response = response.replace("___TEMP_NAME___", full_name)
                # Cleanup any accidental doubling if the LLM wrote "Name Name"
                response = response.replace(f"{full_name} {full_name}", full_name)
                response = response.replace(f"{full_name} Prasad", full_name)
            
            return response
            
        except Exception as e:
            return f"Error processing PDF: {str(e)}"
