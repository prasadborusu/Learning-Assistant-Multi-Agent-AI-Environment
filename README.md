# AI Agent-Based Multi-Agent Learning System

This project is a complete AI-driven Multi-Agent learning platform built with **FastAPI** (Python backend) and a modern **HTML/CSS/JS** frontend. 
It features a **Coordinator Agent** that dynamically delegates user requests to specialized sub-agents based on real-time intent classification.

## Agent Architecture
1. **Coordinator Agent:** Analyzes the prompt and routes it. Also tracks conversation memory.
2. **Query Agent:** Explains concepts and answers theoretical learning questions.
3. **Recommendation Agent:** Suggests books, articles, online courses, and videos.
4. **Quiz Agent:** Generates practice questions to test the user's knowledge.

## Prerequisites
- Python 3.9+
- A Google Gemini API Key (`GEMINI_API_KEY`). Alternatively, the code can be adapted to OpenAI.

## Setup Instructions

1. **Install Dependencies:**
   Navigate into the project folder and install the required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Open the `.env` file in the root directory and add your API key:
   ```env
    HUGGINGFACE_API_KEY="isert your hf token"
   ```

3. **Run the Application:**
   Start the FastAPI standalone ASGI server:
   ```bash
   python app.py
   ```
   Alternatively, you can run it via Uvicorn:
   ```bash
   uvicorn app:app --reload
   ```

4. **Access the System:**
   Open your browser and navigate to
   http://127.0.0.1:8000/

## Advanced Features Included
- **Memory Management:** Keeps track of conversation history securely per session.
- **Dynamic Routing Logs:** The frontend UI visually highlights the routing decision of the Coordinator in real-time.
- **Multilingual Support:** Select from English, Spanish, or French in the dropdown menu to communicate with the agents in different languages.

---
*Developed for Hackathon evaluation demonstrating real AI autonomous multi-agent behavior.*
