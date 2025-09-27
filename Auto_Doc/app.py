"""
Autodoc API - Documentation Generator

This API provides functionality to generate documentation in both .ipynb and .md formats
based on a folder path and template file.
"""

import os
import json
import nbformat
import re
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from fastapi import FastAPI, File, UploadFile, Form, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import shutil
import tempfile
from typing import Optional, List, Dict, Any
import uvicorn
from datetime import datetime
import markdown
from pathlib import Path
import logging

# Import from clarityforge_app
from clarityforge_app.handlers.modelhandler import ModelHandler
from clarityforge_app.handlers.userinterface import UserInterface
from clarityforge_app.handlers.menuhandler import MenuHandler
from clarityforge_app.handlers.preferenceshandler import PreferencesHandler

# Import from utils
from utils import (
    token_provider, 
    PERSONAL_TOKEN, 
    allowed_file, 
    ipynb_to_txt, 
    clean_llm_output, 
    analyze_project_with_llm
)

# Import from open_arena_lib
from open_arena_lib.auth import AuthClient
from open_arena_lib.chat import Chat

app = FastAPI(
    title="Autodoc API",
    description="API for generating documentation from code files",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ALLOWED_EXTENSIONS = {'md', 'txt', 'ipynb'}
TEMP_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'temp')
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'output')
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'clarityforge_app', 'template_doc', 'web_uploads')

# Create necessary folders if they don't exist
os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'autodoc.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DocumentRequest(BaseModel):
    folder_path: str
    template_path: str
    project_name: Optional[str] = None

@app.post("/generate")
async def generate_documentation(
    folder_path: str = Form(...),
    template_file: UploadFile = File(...),
    project_name: Optional[str] = Form(None),
    background_tasks: BackgroundTasks = None
):
    """
    Generate documentation based on folder path and template file
    
    Args:
        folder_path: Path to the project folder
        template_file: Template file for documentation
        
    Returns:
        JSON response with download links for .md and .ipynb files
    """
    try:
        logger.info(f"Documentation generation request received")
        logger.info(f"Folder path: {folder_path}")
        logger.info(f"Project name: {project_name if project_name else 'Not provided'}")
        logger.info(f"Template file: {template_file.filename}")
        
        # Validate folder path
        logger.info("Validating folder path")
        folder_path = os.path.expanduser(folder_path)
        if not os.path.isdir(folder_path):
            logger.error(f"Invalid project folder: {folder_path}")
            raise HTTPException(status_code=400, detail=f"Invalid project folder: {folder_path}")
        
        # Validate template file
        logger.info("Validating template file")
        if not template_file or not allowed_file(template_file.filename):
            logger.error(f"Invalid template file: {template_file.filename if template_file else 'None'}")
            raise HTTPException(status_code=400, detail="Invalid template file")
        
        # Save template file
        logger.info("Saving template file")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"autodoc_{timestamp}_{template_file.filename}"
        template_path = os.path.join(UPLOAD_FOLDER, filename)
        logger.info(f"Template path: {template_path}")
        
        with open(template_path, "wb") as buffer:
            shutil.copyfileobj(template_file.file, buffer)
        logger.info("Template file saved successfully")
        
        # If .ipynb, convert to .txt
        if filename.lower().endswith('.ipynb'):
            logger.info("Converting .ipynb template to .txt")
            txt_template_path = ipynb_to_txt(template_path)
            template_path = txt_template_path
            logger.info(f"Converted template path: {template_path}")
        
        # Read template file
        logger.info("Reading template file")
        with open(template_path, 'r', encoding='utf-8') as f:
            template_text = f.read()
        logger.info(f"Template file read successfully, size: {len(template_text)} characters")
        
        # Setup LLM infrastructure
        logger.info("Setting up LLM infrastructure")
        ui = UserInterface()
        model_handler = ModelHandler()
        preferences_handler = PreferencesHandler(ui)
        config = preferences_handler.load_preferences()
        selected_model = model_handler.get_selected_model()
        workflow_id = model_handler.get_workflow_id(selected_model)
        logger.info(f"Using model: {selected_model} with workflow ID: {workflow_id}")
        
        auth = AuthClient(token_provider=PERSONAL_TOKEN if PERSONAL_TOKEN else token_provider)
        logger.info("LLM infrastructure setup completed")
        
        # Generate documentation
        logger.info(f"Starting project analysis with LLM")
        
        # Try with progressively smaller file sizes if we encounter message size errors
        try:
            logger.info("Attempting documentation generation with default file size limits")
            documentation = analyze_project_with_llm(
                folder_path, 
                template_text, 
                config, 
                auth, 
                workflow_id,
                project_name=project_name
            )
            logger.info("Documentation generation completed successfully with default settings")
        except Exception as e:
            if "message too big" in str(e):
                logger.warning("Message too big error encountered, trying with smaller file size limits")
                try:
                    # Try with smaller limits
                    logger.info("Attempting documentation generation with reduced file size limits (50KB/2MB)")
                    documentation = analyze_project_with_llm(
                        folder_path, 
                        template_text, 
                        config, 
                        auth, 
                        workflow_id,
                        project_name=project_name,
                        max_file_size_kb=50, 
                        max_total_size_mb=2
                    )
                    logger.info("Documentation generation completed successfully with reduced file size")
                except Exception as e2:
                    if "message too big" in str(e2):
                        logger.warning("Still encountering message size issues, trying with minimal file size limits")
                        # Try with even smaller limits as a last resort
                        logger.info("Attempting documentation generation with minimal file size limits (20KB/1MB)")
                        documentation = analyze_project_with_llm(
                            folder_path, 
                            template_text, 
                            config, 
                            auth, 
                            workflow_id,
                            project_name=project_name,
                            max_file_size_kb=20, 
                            max_total_size_mb=1
                        )
                        logger.info("Documentation generation completed successfully with minimal file size")
                    else:
                        raise e2
            else:
                raise e
        
        # Check if documentation was generated successfully
        if not documentation or documentation.strip() == "" or "Error" in documentation[:100]:
            logger.error("LLM returned empty or error response")
            raise HTTPException(status_code=500, detail="Failed to generate documentation. The model did not return a valid response.")
        
        logger.info("Documentation validation passed")
        
        # Create output directory
        output_dir = os.path.join(OUTPUT_FOLDER, timestamp)
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")
        
        # Save markdown file
        file_prefix = project_name if project_name else "GENERATED_DOC"
        # Replace spaces with underscores and remove special characters from project_name
        file_prefix = re.sub(r'[^\w\s]', '', file_prefix).replace(' ', '_')
        
        md_filename = f'{file_prefix}_{timestamp}.md'
        md_path = os.path.join(output_dir, md_filename)
        logger.info(f"Markdown filename: {md_filename}")
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(documentation)
        logger.info(f"Saved markdown file: {md_path}")
        
        # Create .ipynb file from the documentation
        ipynb_filename = f'{file_prefix}_{timestamp}.ipynb'
        ipynb_path = os.path.join(output_dir, ipynb_filename)
        logger.info(f"Jupyter notebook filename: {ipynb_filename}")
        logger.info("Creating Jupyter notebook from documentation")
        nb = new_notebook()
        nb.cells = [new_markdown_cell(documentation)]
        with open(ipynb_path, 'w', encoding='utf-8') as f:
            nbformat.write(nb, f)
        logger.info(f"Saved Jupyter notebook file: {ipynb_path}")
        
        # Clean up temporary template file
        if os.path.exists(template_path):
            logger.info(f"Scheduling cleanup of temporary template file: {template_path}")
            background_tasks.add_task(os.remove, template_path)
        
        # Return download links
        logger.info("Returning download links to client")
        response_content = {
            "success": True,
            "message": "Documentation generated successfully",
            "md_file": f"/download/{timestamp}/{md_filename}",
            "ipynb_file": f"/download/{timestamp}/{ipynb_filename}",
            "timestamp": timestamp,
            "project_name": project_name if project_name else "Not specified"
        }
        logger.info(f"Response content: {response_content}")
        
        return JSONResponse(
            content=response_content,
            status_code=200
        )
    
    except Exception as e:
        logger.error(f"Error generating documentation: {str(e)}")
        # Clean up temporary template file on error
        if 'template_path' in locals() and os.path.exists(template_path):
            try:
                os.remove(template_path)
            except:
                pass
        
        raise HTTPException(status_code=500, detail=f"Error generating documentation: {str(e)}")

@app.get("/download/{timestamp}/{filename}")
async def download_file(timestamp: str, filename: str):
    """
    Download generated documentation file
    
    Args:
        timestamp: Timestamp of the generation
        filename: Name of the file to download
        
    Returns:
        File response with the requested file
    """
    logger.info(f"Download request received for file: {filename}, timestamp: {timestamp}")
    file_path = os.path.join(OUTPUT_FOLDER, timestamp, filename)
    logger.info(f"Looking for file at path: {file_path}")
    
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        raise HTTPException(status_code=404, detail="File not found")
    
    logger.info(f"File found, preparing download response")
    
    response = FileResponse(
        path=file_path,
        filename=filename,
        media_type='application/octet-stream'
    )
    logger.info(f"File download response prepared for: {filename}")
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check request received")
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=5001, reload=True)
