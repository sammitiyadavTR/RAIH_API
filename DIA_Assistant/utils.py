import os
import sys
import json
import requests
from open_arena_lib.auth import AuthClient
from open_arena_lib.file import FileClient
from open_arena_lib.chat import Chat

def default_token_provider():
    """
    Personal Token
    
    """
    print("Attempting to read token file...")
    try:
        with open("DIA_Assistant/token.txt", "r") as file:
            token = file.read().strip()
        print("Token file read successfully")
        return token
    except Exception as e:
        print(f"Error reading token file: {e}")
        raise

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
            "client_id": "6TVQhjfIl8c8jhcYPD7eOKUAZPmG0LPk",
            "client_secret": "J6WNwDu5DHE2sj_aop0-J9BRVbbausKcw6mDPt2ZRU8lw_TsqbnTo1_OuXazsyuh", 
            "audience": "49d70a58-9509-48a2-ae12-4f6e00ceb270",
            "grant_type": "client_credentials"
        }
        response = requests.post('https://auth.thomsonreuters.com/oauth/token', headers=headers, data=data)
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
        auth = AuthClient(token_provider=default_token_provider)
        workflow_id = "89f62481-2a7e-409b-afe3-5c575d83215c"
        
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
