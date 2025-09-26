from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import os
import tempfile
import shutil
from typing import Optional
import uvicorn
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Configuration
HOST = os.getenv("HOST")
PORT = int(os.getenv("PORT"))
RELOAD = os.getenv("RELOAD").lower() == "true"

# Directory Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, os.getenv("UPLOADS_DIR"))
STATIC_DIR = os.path.join(BASE_DIR, os.getenv("STATIC_DIR"))

# CORS Configuration
ALLOW_ORIGINS = os.getenv("ALLOW_ORIGINS")
ALLOW_CREDENTIALS = os.getenv("ALLOW_CREDENTIALS").lower() == "true"
ALLOW_METHODS = os.getenv("ALLOW_METHODS")
ALLOW_HEADERS = os.getenv("ALLOW_HEADERS")

from utils import process_dia_request

class TextAnalysisRequest(BaseModel):
    text_input: str

app = FastAPI(
    title="AI-Assisted DIA API",
    description="API for AI-assisted Data Impact Assessment",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[ALLOW_ORIGINS],  # Allows all origins by default
    allow_credentials=ALLOW_CREDENTIALS,
    allow_methods=[ALLOW_METHODS],  # Allows all methods by default
    allow_headers=[ALLOW_HEADERS],  # Allows all headers by default
)

# Create necessary directories if they don't exist

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(STATIC_DIR, exist_ok=True)

# Mount the static files directory
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the HTML interface for the API"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/status")
async def status():
    """API status endpoint to check if the API is running"""
    return {"message": "AI-Assisted DIA API is running"}

@app.post("/analyze")
async def analyze_data(
    file: Optional[UploadFile] = File(None),
    text_input: Optional[str] = Form(None)
):
    """
    Analyze data using AI-assisted DIA
    
    Parameters:
    - file: Optional file upload
    - text_input: Optional text input
    
    Returns:
    - JSON response with analysis result
    """
    if not file and not text_input:
        raise HTTPException(status_code=400, detail="Either file or text input must be provided")
    
    # Handle file upload if provided
    uploaded_file_path = None
    if file:
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, dir=UPLOADS_DIR, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                uploaded_file_path = temp_file.name
                # Copy the uploaded file to the temporary file
                shutil.copyfileobj(file.file, temp_file)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error processing file upload: {str(e)}")
        finally:
            file.file.close()
    
    try:
        # Process the request
        result = process_dia_request(uploaded_file_path, text_input)
        
        # Clean up the temporary file
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            os.unlink(uploaded_file_path)
        
        return JSONResponse(content={"result": result})
    except Exception as e:
        # Clean up the temporary file in case of error
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            os.unlink(uploaded_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
