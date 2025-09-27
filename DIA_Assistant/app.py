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
import logging
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(LOG_DIR, f"dia_assistant_{datetime.now().strftime('%Y%m%d')}.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

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

app = FastAPI(
    title="AI-Assisted DIA API",
    description="API for AI-assisted Data Impact Assessment",
    version="1.0.0"
)

# Log application startup
logger.info("=== DIA Assistant API Starting ===")
logger.info(f"Host: {HOST}, Port: {PORT}, Reload: {RELOAD}")
logger.info(f"Uploads Directory: {UPLOADS_DIR}")
logger.info(f"Static Directory: {STATIC_DIR}")

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
    logger.info("Root endpoint accessed - serving web interface")
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.get("/api/status")
async def status():
    """API status endpoint to check if the API is running"""
    logger.info("API status check requested")
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
    # Log the incoming request
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    logger.info(f"[{request_id}] DIA Analysis request received")
    logger.info(f"[{request_id}] File provided: {'Yes' if file else 'No'}")
    logger.info(f"[{request_id}] Text input provided: {'Yes' if text_input else 'No'}")
    
    if file:
        logger.info(f"[{request_id}] File details - Name: {file.filename}, Size: {file.size if hasattr(file, 'size') else 'Unknown'}")
    
    if text_input:
        logger.info(f"[{request_id}] Text input length: {len(text_input)} characters")
    
    if not file and not text_input:
        logger.error(f"[{request_id}] Request rejected: No file or text input provided")
        raise HTTPException(status_code=400, detail="Either file or text input must be provided")
    
    # Handle file upload if provided
    uploaded_file_path = None
    if file:
        logger.info(f"[{request_id}] Processing file upload: {file.filename}")
        try:
            # Create a temporary file
            with tempfile.NamedTemporaryFile(delete=False, dir=UPLOADS_DIR, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                uploaded_file_path = temp_file.name
                logger.info(f"[{request_id}] Created temporary file: {uploaded_file_path}")
                # Copy the uploaded file to the temporary file
                shutil.copyfileobj(file.file, temp_file)
                logger.info(f"[{request_id}] File uploaded successfully to temporary location")
        except Exception as e:
            logger.error(f"[{request_id}] File upload failed: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error processing file upload: {str(e)}")
        finally:
            file.file.close()
    
    try:
        logger.info(f"[{request_id}] Starting DIA analysis processing...")
        start_time = datetime.now()
        
        # Process the request
        result = process_dia_request(uploaded_file_path, text_input)
        
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        logger.info(f"[{request_id}] DIA analysis completed successfully in {processing_time:.2f} seconds")
        logger.info(f"[{request_id}] Result length: {len(result) if result else 0} characters")
        
        # Clean up the temporary file
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            logger.info(f"[{request_id}] Cleaning up temporary file: {uploaded_file_path}")
            os.unlink(uploaded_file_path)
        
        logger.info(f"[{request_id}] DIA analysis request completed successfully")
        return JSONResponse(content={"result": result})
    except Exception as e:
        logger.error(f"[{request_id}] DIA analysis failed with error: {str(e)}")
        # Clean up the temporary file in case of error
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            logger.info(f"[{request_id}] Cleaning up temporary file after error: {uploaded_file_path}")
            os.unlink(uploaded_file_path)
        raise HTTPException(status_code=500, detail=f"Error processing request: {str(e)}")

if __name__ == "__main__":
    logger.info("=== Starting DIA Assistant API Server ===")
    logger.info(f"Server will start on {HOST}:{PORT} with reload={RELOAD}")
    uvicorn.run("app:app", host=HOST, port=PORT, reload=RELOAD)
