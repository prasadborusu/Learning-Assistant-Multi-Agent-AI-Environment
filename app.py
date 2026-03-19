from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import shutil

from agents.coordinator import CoordinatorAgent
from memory.memory_manager import MemoryManager

# Initialize components
coordinator = CoordinatorAgent()
memory_manager = MemoryManager()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Multi-Agent Learning System", description="A personalized learning system driven by autonomous AI agents.")

# Enable CORS (optional for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount the static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def read_index():
    return FileResponse("static/index.html")

class ChatRequest(BaseModel):
    prompt: str
    session_id: str = "default-session"

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...), session_id: str = Form("default-session")):
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
    
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # Summarize the PDF
        summary = coordinator.pdf_agent.process_pdf(file_path)
        
        # Add to history
        memory_manager.add_message(session_id, "user", f"[Uploaded PDF: {file.filename}]")
        memory_manager.add_message(session_id, "agent", summary)
        
        return {
            "agent_key": "pdf",
            "agent": "PDF Analyst",
            "decision": "PDF Summarization",
            "response": summary,
            "filename": file.filename
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup file after processing
        if os.path.exists(file_path):
            os.remove(file_path)

@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    try:
        # Retrieve history
        context = memory_manager.get_history(request.session_id)
        
        # Add user message to memory
        memory_manager.add_message(request.session_id, "user", request.prompt)
        
        # Process via Coordinator
        response_data = coordinator.process_request(request.prompt, context)
        
        # Add agent response to memory
        memory_manager.add_message(request.session_id, "agent", response_data["response"])
        
        return response_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
