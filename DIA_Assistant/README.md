# DIA_Assistant

**Data Impact Assessment Assistant - Part of Responsible AI Hub (RAIH)**

A sophisticated FastAPI-based service that provides AI-powered Data Impact Assessment (DIA) capabilities. The system analyzes documents, text inputs, and data processing scenarios to help organizations understand and mitigate potential impacts of their data handling practices.

## 🚀 Overview

DIA_Assistant is an intelligent assessment tool that leverages Thomson Reuters OpenArena platform to provide comprehensive analysis of data impact scenarios. It supports multiple input methods and delivers detailed assessments to help organizations make informed decisions about data processing activities.

## ✨ Key Features

- 📄 **Multi-Input Support** - Accepts both file uploads (PDF, documents) and text input
- 🧠 **AI-Powered Analysis** - Uses advanced LLM models via Thomson Reuters OpenArena
- 🌐 **Web Interface** - User-friendly web UI for easy testing and interaction
- 📊 **Comprehensive Assessments** - Detailed impact analysis with actionable insights
- 🔒 **Secure File Handling** - Temporary file processing with automatic cleanup
- 📱 **Dual API Endpoints** - Support for both JSON and form-data requests
- 🎯 **RESTful Design** - Clean, well-documented API architecture
- 📋 **Interactive Documentation** - Built-in Swagger UI and ReDoc interfaces

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (for local installation) OR Docker (for containerized deployment)
- Access to Thomson Reuters OpenArena platform
- Valid authentication credentials

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker

1. **Navigate to DIA_Assistant directory:**
   ```bash
   cd DIA_Assistant
   ```

2. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual values
   # Required: CLIENT_ID, CLIENT_SECRET for OpenArena access
   ```

3. **Deploy with Docker Compose:**
   ```bash
   # Build and start the service
   docker-compose up -d
   
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs -f dia-assistant
   
   # Stop the service
   docker-compose down
   ```

4. **Manual Docker commands (alternative):**
   ```bash
   # Build the image
   docker build -t dia-assistant .
   
   # Run the container
   docker run -p 8000:8000 --env-file .env dia-assistant
   ```

The API will be available at `http://localhost:8000`

### Docker Features
- ✅ **Production Ready** - Optimized for production deployment
- ✅ **Secure Environment** - Non-root user and minimal attack surface
- ✅ **Persistent Storage** - Volume mounts for uploads and static files
- ✅ **Health Monitoring** - Built-in health checks
- ✅ **Auto Restart** - Automatic service recovery
- ✅ **Resource Management** - Configurable CPU and memory limits

## 🐍 Local Python Installation (Alternative)

### Installation Steps

1. **Navigate to DIA_Assistant directory:**
   ```bash
   cd DIA_Assistant
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file with the following configuration:
   ```env
   # Server Configuration
   HOST=0.0.0.0
   PORT=8000
   RELOAD=true
   
   # Directory Configuration
   UPLOADS_DIR=uploads
   STATIC_DIR=static
   
   # CORS Configuration
   ALLOW_ORIGINS=*
   ALLOW_CREDENTIALS=true
   ALLOW_METHODS=*
   ALLOW_HEADERS=*
   
   # Thomson Reuters OpenArena Configuration
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   AUDIENCE=your_audience
   GRANT_TYPE=client_credentials
   ```

4. **Run the application:**
   ```bash
   python main.py
   ```

The API will be available at `http://localhost:8000`

## 🔧 API Endpoints

### 1. Web Interface
```http
GET /
```
**Description:** Serves the interactive web interface for testing the DIA Assistant

**Response:** HTML page with file upload and text input capabilities

### 2. API Status Check
```http
GET /api/status
```
**Description:** Health check endpoint to verify API availability

**Response:**
```json
{
  "message": "AI-Assisted DIA API is running"
}
```

### 3. Data Impact Analysis (Form Data)
```http
POST /analyze
```
**Description:** Analyzes data impact scenarios using uploaded files and/or text input

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (optional, file): Document file (PDF, DOC, TXT, etc.)
- `text_input` (optional, string): Text description of data processing scenario

**Note:** At least one parameter must be provided

**Example Request:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@document.pdf" \
  -F "text_input=Analyze data collection impact for mobile app"
```

**Success Response:**
```json
{
  "result": "Comprehensive data impact analysis with recommendations and risk assessment..."
}
```

**Error Response:**
```json
{
  "detail": "Either file or text input must be provided"
}
```

### 4. Text-Only Analysis (JSON)
```http
POST /analyze-text
```
**Description:** Analyzes text-only data impact scenarios using JSON input

**Content-Type:** `application/json`

**Request Body:**
```json
{
  "text_input": "Description of data processing scenario to analyze"
}
```

**Example Request:**
```bash
curl -X POST "http://localhost:8000/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{"text_input": "Analyze privacy impact of user behavior tracking"}'
```

**Success Response:**
```json
{
  "result": "Detailed analysis of privacy implications and mitigation strategies..."
}
```

## 💼 Use Cases

### Data Processing Scenarios
- **Privacy Impact Assessments** - Evaluate privacy implications of data collection
- **Data Transfer Analysis** - Assess risks in cross-border data transfers
- **Third-Party Integration** - Analyze impacts of sharing data with vendors
- **Data Retention Policies** - Evaluate data lifecycle management practices
- **Consent Management** - Review consent mechanisms and user rights

### Document Analysis
- **Policy Reviews** - Analyze existing privacy policies and data handling procedures
- **Contract Assessment** - Review data processing agreements and vendor contracts
- **Compliance Checks** - Verify alignment with GDPR, CCPA, and other regulations
- **Risk Documentation** - Process risk assessment reports and mitigation plans

## 🎯 Example Usage

### Using cURL

**Text-only analysis:**
```bash
curl -X POST "http://localhost:8000/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{"text_input": "Analyze the privacy impact of implementing user behavior tracking in our e-commerce platform"}'
```

**File upload with context:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@privacy_policy.pdf" \
  -F "text_input=Review this policy for GDPR compliance gaps"
```

**Document-only analysis:**
```bash
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@data_processing_agreement.pdf"
```

### Using Python Requests

```python
import requests

# Text-only analysis
response = requests.post(
    "http://localhost:8000/analyze-text",
    json={"text_input": "Evaluate data retention risks for customer analytics platform"}
)
print(response.json())

# File upload with additional context
with open("privacy_policy.pdf", "rb") as f:
    response = requests.post(
        "http://localhost:8000/analyze",
        files={"file": f},
        data={"text_input": "Focus on international data transfer provisions"}
    )
print(response.json())
```

### Using Python with Open Arena Library

```python
from utils import process_dia_request

# Direct function call (for integration)
result = process_dia_request(
    uploaded_file_path="path/to/document.pdf",
    text_input="Analyze this document for compliance risks"
)
print(result)
```

## 🌐 Web Interface

The DIA Assistant includes a modern, responsive web interface accessible at `http://localhost:8000/`

**Features:**
- **File Upload** - Drag-and-drop or browse for documents
- **Text Input** - Rich text area for scenario descriptions
- **Real-time Analysis** - Live processing with loading indicators
- **Formatted Results** - Clean, readable analysis output
- **Error Handling** - User-friendly error messages
- **Mobile Responsive** - Works on all device sizes

## 📚 Interactive API Documentation

FastAPI provides comprehensive, interactive API documentation:

- **Swagger UI:** `http://localhost:8000/docs`
- **ReDoc:** `http://localhost:8000/redoc`

**Features:**
- **Try It Out** - Test endpoints directly in the browser
- **Request/Response Examples** - Complete API specifications
- **Parameter Documentation** - Detailed parameter descriptions
- **Authentication Info** - Security requirements and setup
- **Download OpenAPI Spec** - Export API specification

## 🏗️ Architecture Overview

### Core Components

1. **FastAPI Application** (`main.py`)
   - RESTful API endpoints
   - Request validation and processing
   - File upload handling
   - Error management and logging

2. **Analysis Engine** (`utils.py`)
   - Thomson Reuters OpenArena integration
   - Document processing and analysis
   - Response formatting and cleaning
   - Authentication management

3. **Web Interface** (`static/index.html`)
   - Modern, responsive UI
   - File upload with drag-and-drop
   - Real-time form validation
   - Result display and formatting

### Integration Points

- **Thomson Reuters OpenArena** - AI/LLM processing platform
- **File Processing** - Temporary file handling with cleanup
- **Environment Configuration** - Flexible deployment settings
- **CORS Support** - Cross-origin resource sharing for web clients

## 📁 File Structure

```
DIA_Assistant/
├── main.py                    # Main FastAPI application
├── utils.py                   # OpenArena integration and processing
├── static/
│   └── index.html            # Web interface
├── uploads/                  # Temporary file storage (auto-created)
├── .env                      # Environment configuration
├── .env.example              # Environment template
├── Dockerfile                # Docker container definition
├── docker-compose.yml        # Docker Compose configuration
├── .dockerignore            # Docker ignore rules
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## 🔍 Advanced Features

### File Processing
- **Multiple Formats** - Support for PDF, DOC, TXT, and other document types
- **Secure Upload** - Temporary file handling with automatic cleanup
- **Size Validation** - Configurable file size limits
- **Error Handling** - Graceful handling of corrupt or unsupported files

### AI Analysis
- **Context Awareness** - Combines file content with text input for comprehensive analysis
- **Structured Output** - Formatted responses with clear recommendations
- **Risk Assessment** - Identifies and categorizes potential data impacts
- **Compliance Focus** - Emphasizes regulatory requirements and best practices

### Security Features
- **Environment Variables** - Secure credential management
- **Temporary Files** - Automatic cleanup of uploaded files
- **CORS Configuration** - Configurable cross-origin policies
- **Input Validation** - Request validation and sanitization

## 🛠️ Dependencies

### Core Dependencies
- **FastAPI** - Modern, fast web framework for building APIs
- **uvicorn** - ASGI server for running FastAPI applications
- **python-multipart** - File upload handling
- **python-dotenv** - Environment variable management

### AI/ML Integration
- **open_arena_lib** - Thomson Reuters OpenArena platform integration
- **requests** - HTTP client for API communications

### Utility Libraries
- **pydantic** - Data validation and parsing using Python type hints
- **tempfile** - Secure temporary file operations
- **shutil** - High-level file operations

## 🐛 Troubleshooting

### Common Issues

**1. Authentication Errors**
- Verify `CLIENT_ID` and `CLIENT_SECRET` in `.env` file
- Check Thomson Reuters OpenArena credentials
- Ensure proper audience configuration

**2. File Upload Problems**
- Check file size limits and format support
- Verify `uploads/` directory permissions
- Ensure sufficient disk space for temporary files

**3. Web Interface Issues**
- Confirm static files are properly mounted
- Check browser console for JavaScript errors
- Verify CORS configuration for cross-origin requests

**4. API Connection Failures**
- Test OpenArena connectivity
- Check network firewall settings
- Verify authentication token validity

### Debug Information
- **Application Logs** - Check console output for detailed error messages
- **HTTP Status Codes** - Use appropriate error codes for troubleshooting
- **Environment Variables** - Verify all required variables are set
- **File Permissions** - Ensure proper read/write access to directories

## 📈 Performance Considerations

- **File Processing** - Temporary files are automatically cleaned up
- **Memory Management** - Efficient handling of large document uploads
- **Async Operations** - Non-blocking request processing
- **Resource Limits** - Configurable CPU and memory constraints
- **Connection Pooling** - Efficient HTTP client management

## 🚀 Deployment Options

### Development Environment
```bash
# Quick local development
python main.py
```

### Production with Docker
```bash
# Production deployment
docker-compose up -d
```

### Cloud Deployment
- **Container Registry** - Push to your preferred registry
- **Kubernetes** - Deploy with included manifests
- **Load Balancing** - Scale horizontally for high availability
- **Monitoring** - Integrate with observability platforms

## 📞 Support

For issues and questions:
1. **Application Logs** - Check console output for detailed error information
2. **Environment Configuration** - Verify all required variables are properly set
3. **API Documentation** - Review endpoints at `http://localhost:8000/docs`
4. **OpenArena Platform** - Contact Thomson Reuters for platform-specific issues
5. **GitHub Issues** - Report bugs and feature requests

## 🎯 Best Practices

### Security
- **Environment Variables** - Never hardcode credentials
- **File Validation** - Always validate uploaded files
- **Input Sanitization** - Sanitize all user inputs
- **Regular Updates** - Keep dependencies updated

### Performance
- **File Cleanup** - Implement proper temporary file management
- **Request Validation** - Validate requests early in the pipeline
- **Error Handling** - Provide meaningful error messages
- **Monitoring** - Implement health checks and logging

### Integration
- **API Versioning** - Plan for API evolution
- **Documentation** - Keep API docs updated
- **Testing** - Implement comprehensive test coverage
- **Monitoring** - Set up observability and alerting

---

**Part of the Thomson Reuters Responsible AI Hub (RAIH) Initiative**  
*Empowering responsible data practices through AI-driven impact assessment*
