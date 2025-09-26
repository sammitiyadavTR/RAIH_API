from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import re
import markdown
import uvicorn
import sys
import os

from OpenArena_ChatbotChain import SimpleRouterAgent

app = FastAPI()

try:
    router = SimpleRouterAgent(confidence_threshold=0.36)
    print("Router agent initialized successfully!")
except Exception as e:
    print(f"Error initializing router agent: {e}")
    router = None

class ChatbotRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"status": "success", "message": "FastAPI server is running"}

@app.post("/chatbot")
async def chatbot(request: ChatbotRequest):
    try:
        user_message = request.message.strip()

        if not user_message:
            return JSONResponse(status_code=400, content={
                'status': 'error',
                'message': 'Please provide a message'
            })

        if user_message.lower() == 'ping':
            return { 'status': 'success', 'message': 'Server is running' }

        if router is None:
            return JSONResponse(status_code=500, content={
                'status': 'error',
                'message': 'Router agent is not available'
            })

        print(f"DEBUG: Processing query: {user_message}")
        result = router.router.route_query(user_message)
        print(f"DEBUG: Routing result: {result}")

        if result['success']:
            formatted_response = format_chatbot_response(result['response'])
            return {
                'status': 'success',
                'message': formatted_response,
                'debug_info': {
                    'agent_used': result['agent_used'],
                    'classification': result['classification'],
                    'execution_time': result['execution_time']
                }
            }
        else:
            return JSONResponse(status_code=500, content={
                'status': 'error',
                'message': f"Routing failed: {result.get('error', 'Unknown error')}",
                'debug_info': result
            })

    except Exception as e:
        print(f"DEBUG: Exception in chatbot route: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(status_code=500, content={
            'status': 'error',
            'message': f'Sorry, I encountered an error: {str(e)}'
        })

def format_chatbot_response(response):
    """Format the router agent response for chatbot display"""
    if not response:
        return "I'm sorry, I couldn't generate a response."
    response = response.strip()
    response = re.sub(r'^\s*ANALYSIS RESULT:\s*', '', response)
    response = re.sub(r'^=+\s*', '', response)
    response = re.sub(r'\s*=+$', '', response)
    html = markdown.markdown(response, extensions=['extra', 'nl2br'])
    return html

if __name__ == "__main__":
    try:
        uvicorn.run("app:app", host="0.0.0.0", port=5000, reload=True)
    finally:
        if router:
            router.close()