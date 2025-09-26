import os
import sys
import json
import requests
from dotenv import load_dotenv
from open_arena_lib.auth import AuthClient
from open_arena_lib.file import FileClient
from open_arena_lib.chat import Chat

# Load environment variables from .env file
load_dotenv()

# Authentication Configuration
AUTH_URL = os.getenv("AUTH_URL")
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
AUDIENCE = os.getenv("AUDIENCE")
GRANT_TYPE = os.getenv("GRANT_TYPE")

# Workflow Configuration
WORKFLOW_ID = os.getenv("WORKFLOW_ID")

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

def process_dia_request(uploaded_file_path=None, text_input=None):
    """
    Process a Data Impact Assessment request
    
    Parameters:
    - uploaded_file_path: Path to the uploaded file (optional)
    - text_input: Text input for analysis (optional)
    
    Returns:
    - Analysis result as a string
    """
    try:
        # Initialize authentication
        auth = AuthClient(token_provider=PERSONAL_TOKEN if PERSONAL_TOKEN else token_provider)
        workflow_id = WORKFLOW_ID
        
        # Initialize file client
        fc = FileClient(auth=auth)
        
        # Initialize chat
        chat = Chat(auth=auth, workflow_id=workflow_id)
        
        # If a file was uploaded, process it
        if uploaded_file_path and os.path.exists(uploaded_file_path):
            file_uuid = fc.upload_file(uploaded_file_path, workflow_id=workflow_id)
            chat.add_file_uuid(file_uuid)
        
        # Prepare the query based on inputs
        if text_input and uploaded_file_path:
            query = f"Based on the uploaded document and the following description, provide a detailed analysis and answer: {text_input}"
        elif text_input:
            query = f"Based on the following description, provide a detailed analysis and answer: {text_input}"
        elif uploaded_file_path:
            query = "Provide a detailed analysis of the uploaded document."
        else:
            query = "Provide a detailed answer."
        
        # Get response from chat
        response = chat.chat(query)
        
        if response and "answer" in response:
            return response["answer"]
        else:
            return "No response received from the AI service."
            
    except Exception as e:
        raise Exception(f"Error processing DIA request: {str(e)}")
