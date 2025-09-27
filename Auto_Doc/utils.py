import os
import sys
import json
import requests
import re
import nbformat
import tempfile
import logging
from dotenv import load_dotenv
from pathlib import Path

# Authentication Configuration
AUTH_URL = os.getenv("AUTH_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUDIENCE = os.getenv("AUDIENCE")
GRANT_TYPE = os.getenv("GRANT_TYPE")

# Token Configuration
PERSONAL_TOKEN = os.getenv("PERSONAL_TOKEN")

def token_provider():
    """
    Load authentication token from Service Account
    
    Returns:
    - Access token string
    """
    try:
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }

        data = {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET, 
            "audience": AUDIENCE,
            "grant_type": GRANT_TYPE
        }
        response = requests.post(AUTH_URL, headers=headers, data=data)
        token = json.loads(response.text)
        return token["access_token"]
    except Exception as e:
        raise Exception(f"Error while retrieving tokens: {str(e)}")

def allowed_file(filename):
    """Check if the file extension is allowed"""
    ALLOWED_EXTENSIONS = {'md', 'txt', 'ipynb'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ipynb_to_txt(ipynb_path):
    """Convert .ipynb file to .txt for template processing"""
    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            notebook = json.load(f)
        
        txt_content = ""
        for cell in notebook.get('cells', []):
            if cell.get('cell_type') == 'markdown':
                txt_content += ''.join(cell.get('source', [])) + "\n\n"
        
        txt_path = ipynb_path.rsplit('.', 1)[0] + '.txt'
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        return txt_path
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Error converting notebook to text: {e}")
        raise e

def clean_llm_output(content):
    """Clean LLM output by removing instructions"""
    # Remove any lines that look like instructions to the model
    lines = content.split('\n')
    cleaned_lines = []
    in_instruction_block = False
    
    for line in lines:
        if re.match(r'^(Instructions|Note to model|Note:|Please):', line, re.IGNORECASE):
            in_instruction_block = True
            continue
        
        if in_instruction_block and (line.strip() == '' or line.startswith('---')):
            in_instruction_block = False
            continue
            
        if not in_instruction_block:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

def analyze_project_with_llm(project_folder, template_text, config, auth, workflow_id, project_name=None, max_file_size_kb=100, max_total_size_mb=5):
    """
    Analyze project with LLM and generate documentation
    
    Args:
        project_folder: Path to the project folder
        template_text: Template text for documentation
        config: Configuration for the LLM
        auth: Authentication client
        workflow_id: Workflow ID for the LLM
        project_name: Name of the project to include in documentation
        max_file_size_kb: Maximum size of individual files to include (in KB) - not used in this implementation
        max_total_size_mb: Maximum total size of all files combined (in MB) - not used in this implementation
        
    Returns:
        Generated documentation as string
    """
    try:
        logger = logging.getLogger(__name__)
        logger.info(f"Starting project analysis with LLM for project: {project_name if project_name else 'Unnamed'}")
        logger.info(f"Project folder: {project_folder}")
        logger.info(f"Max file size: {max_file_size_kb}KB, Max total size: {max_total_size_mb}MB")
        
        # Initialize Chat with authentication and workflow ID
        from open_arena_lib.chat import Chat
        logger.info("Initializing Chat with authentication and workflow ID")
        
        system_prompt = f"You are an expert documentation generator. Analyze the following project and fill the following template. Return the filled template as markdown or plain text."
        if project_name:
            system_prompt += f"\n\nPROJECT_NAME: {project_name}"
        
        system_prompt += f"\n\nTEMPLATE:\n{template_text}\n\nPROJECT_PATH: {project_folder}"
        
        chat = Chat(auth=auth, workflow_id=workflow_id, model_params={
            "system_prompt": system_prompt,
            "enable_reasoning": json.dumps(config.get("enable_reasoning", True))
        }, max_history=config.get("chat_history_length"))
        
        logger.info("Chat initialized successfully")
        
        # Send query to LLM
        logger.info(f"Sending documentation request to LLM for project: {project_folder}")
        query = f"Fill the template for the project"
        if project_name:
            query += f" named '{project_name}'"
        query += f" at {project_folder}. Return the completed document as markdown or plain text."
        
        logger.info(f"Query: {query}")
        logger.info("Sending chat request to LLM...")
        
        response = chat.chat(query)
        logger.info("Received documentation from LLM")
        
        logger.info("Processing LLM response")
        if isinstance(response, dict) and "answer" in response:
            logger.info("Response is a dictionary with 'answer' key")
            result = response["answer"]
        elif hasattr(response, 'content'):
            logger.info("Response has 'content' attribute")
            result = response.content
        elif isinstance(response, str):
            logger.info("Response is a string")
            result = response
        else:
            logger.error(f"Unexpected response type: {type(response)}")
            raise ValueError(f"Unexpected response type: {type(response)}")
        
        # Add project name at the beginning of the documentation if provided
        if project_name:
            logger.info(f"Adding project name '{project_name}' to the beginning of documentation")
            result = f"# {project_name}\n\n{result}"
            
        logger.info("Documentation processing completed successfully")
        return result
            
    except Exception as e:
        logger.error(f"Error analyzing project with LLM: {e}")
        raise e
