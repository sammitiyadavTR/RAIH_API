# AI-Assisted DIA FastAPI Application

This is a FastAPI application that provides an API for AI-assisted Data Impact Assessment (DIA). It uses the OpenArena AI service to analyze documents and text inputs.

## Setup

### Local Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Run the application:

```bash
python main.py
```

The API will be available at `http://localhost:8000`.

### Docker Setup

1. Build the Docker image:

```bash
docker build -t dia-fastapi-app .
```

2. Run the Docker container:

```bash
docker run -p 8000:8000 dia-fastapi-app
```

The API will be available at `http://localhost:8000`.

## API Endpoints

### Root Endpoint

- **URL**: `/`
- **Method**: `GET`
- **Description**: Check if the API is running
- **Response**: 
  ```json
  {
    "message": "AI-Assisted DIA API is running"
  }
  ```

### Analyze Data

- **URL**: `/analyze`
- **Method**: `POST`
- **Description**: Analyze data using AI-assisted DIA
- **Parameters**:
  - `file` (optional): File upload
  - `text_input` (optional): Text input
- **Note**: At least one of `file` or `text_input` must be provided
- **Response**:
  ```json
  {
    "result": "Analysis result from the AI service"
  }
  ```

## Example Usage

### Using cURL

```bash
# Analyze with text input only
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -F "text_input=Analyze the impact of collecting user data for a new mobile application"

# Analyze with file upload
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -F "file=@/path/to/your/document.pdf"

# Analyze with both file and text input
curl -X POST "http://localhost:8000/analyze" \
  -H "accept: application/json" \
  -F "file=@/path/to/your/document.pdf" \
  -F "text_input=Additional context for the analysis"
```

### Using Python Requests

```python
import requests

# Analyze with text input only
response = requests.post(
    "http://localhost:8000/analyze",
    data={"text_input": "Analyze the impact of collecting user data for a new mobile application"}
)
print(response.json())

# Analyze with file upload
with open("/path/to/your/document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": f}
    )
print(response.json())

# Analyze with both file and text input
with open("/path/to/your/document.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        data={"text_input": "Additional context for the analysis"},
        files={"file": f}
    )
print(response.json())
```

## Web Interface

The API comes with a simple web interface that allows you to test it directly from your browser. Once the application is running, you can access it at:

- Web Interface: `http://localhost:8000/`

This interface provides a form where you can enter text input and/or upload a file for analysis.

## Interactive API Documentation

FastAPI provides automatic interactive API documentation. Once the application is running, you can access:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

These interfaces allow you to explore and test the API endpoints directly from your browser.

## API Endpoints Reference

- **GET /** - Web interface for testing the API
- **GET /api/status** - Check if the API is running
- **POST /analyze** - Analyze data using AI-assisted DIA
