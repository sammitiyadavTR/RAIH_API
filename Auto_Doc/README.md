# Auto_Doc API

**Automated Documentation Generator - Part of Responsible AI Hub (RAIH)**

A powerful FastAPI-based service that automatically generates comprehensive documentation from code repositories using advanced LLM models and customizable templates.

## 🚀 Overview

Auto_Doc is an intelligent documentation generation tool that analyzes your entire codebase and creates structured, professional documentation based on custom templates. It leverages the Thomson Reuters OpenArena platform for AI-powered code analysis and understanding.

## ✨ Key Features

- 📝 **Intelligent Code Analysis** - Analyzes entire code repositories using advanced LLM models
- 🎯 **Template-Driven Generation** - Uses customizable templates to guide documentation structure and format
- 📋 **Multiple Template Formats** - Supports `.md`, `.txt`, and `.ipynb` template files
- 📊 **Dual Output Formats** - Generates documentation in both Markdown (`.md`) and Jupyter Notebook (`.ipynb`) formats
- 🔄 **Smart File Management** - Automatically handles large projects with intelligent file size management
- 🌐 **RESTful API** - Clean, well-documented API endpoints for easy integration
- 📁 **Organized Output** - Timestamped output directories for version management
- 🛡️ **Error Handling** - Robust error handling with progressive file size reduction for large projects
- 🔒 **Secure Processing** - Temporary file handling with automatic cleanup

## 🔧 API Endpoints

### 1. Generate Documentation

```http
POST /generate
```

**Description:** Analyzes a code repository and generates comprehensive documentation using a custom template.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `folder_path` (required, form field): Absolute path to the local code repository to analyze
- `template_file` (required, file upload): Template file in `.md`, `.txt`, or `.ipynb` format
- `project_name` (optional, form field): Name of the project to include in the documentation

**Example Request:**
```bash
curl -X POST "http://localhost:5001/generate" \
  -F "folder_path=/path/to/your/project" \
  -F "template_file=@template.md" \
  -F "project_name=My Awesome Project"
```

**Success Response:**
```json
{
  "success": true,
  "message": "Documentation generated successfully",
  "md_file": "/download/20250927_143022/My_Awesome_Project_20250927_143022.md",
  "ipynb_file": "/download/20250927_143022/My_Awesome_Project_20250927_143022.ipynb",
  "timestamp": "20250927_143022",
  "project_name": "My Awesome Project"
}
```

**Error Response:**
```json
{
  "detail": "Invalid project folder: /invalid/path"
}
```

### 2. Download Generated Files

```http
GET /download/{timestamp}/{filename}
```

**Description:** Downloads the generated documentation files.

**Parameters:**
- `timestamp` (path parameter): Timestamp from the generation response
- `filename` (path parameter): Name of the file to download

**Example Request:**
```bash
curl -X GET "http://localhost:5001/download/20250927_143022/My_Project_20250927_143022.md" \
  -o "documentation.md"
```

**Response:** File download with appropriate headers

### 3. Health Check

```http
GET /health
```

**Description:** Verifies that the API service is running and healthy.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-09-27T14:30:22.123456"
}
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+ (for local installation) OR Docker (for containerized deployment)
- Access to Thomson Reuters OpenArena platform
- Valid authentication credentials

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker

1. **Navigate to Auto_Doc directory:**
   ```bash
   cd Auto_Doc
   ```

2. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual values
   # Required: CLIENT_ID, CLIENT_SECRET, AUDIENCE
   ```

3. **Deploy with one command:**
   
   **Linux/Mac:**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```
   
   **Windows:**
   ```batch
   deploy.bat
   ```

4. **Manual Docker commands (alternative):**
   ```bash
   # Build and start the service
   docker-compose up -d
   
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs -f autodoc
   
   # Stop the service
   docker-compose down
   ```

The API will be available at `http://localhost:5001`

### Docker Features
- ✅ **Isolated Environment** - Runs in secure container
- ✅ **Persistent Storage** - Volumes for output, logs, and temp files
- ✅ **Health Checks** - Automatic health monitoring
- ✅ **Resource Limits** - CPU and memory constraints
- ✅ **Auto Restart** - Restarts on failure
- ✅ **Easy Deployment** - One-command setup

## 🐍 Local Python Installation (Alternative)

### Installation

1. **Navigate to Auto_Doc directory:**
   ```bash
   cd Auto_Doc
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the Auto_Doc directory:
   ```env
   AUTH_URL=your_auth_url
   CLIENT_ID=your_client_id
   CLIENT_SECRET=your_client_secret
   AUDIENCE=your_audience
   GRANT_TYPE=client_credentials
   PERSONAL_TOKEN=your_personal_token  # Optional
   ```

4. **Run the API:**
   ```bash
   python app.py
   ```

The API will be available at `http://localhost:5001`

### FastAPI Documentation
- **Interactive API Docs:** `http://localhost:5001/docs`
- **Alternative Docs:** `http://localhost:5001/redoc`

## 📝 Template Guidelines

### Template Format
Templates can be in any of these formats:
- **Markdown (`.md`)** - Standard markdown format
- **Text (`.txt`)** - Plain text format
- **Jupyter Notebook (`.ipynb`)** - Only markdown cells are used

### Template Example
```markdown
# Project Documentation

## Overview
[Provide project overview here]

## Architecture
[Describe the system architecture]

## API Endpoints
[List and describe API endpoints]

## Setup Instructions
[Include setup and installation steps]

## Usage Examples
[Provide usage examples]
```

### Template Variables
The LLM will automatically:
- Fill in template sections based on code analysis
- Add project name if provided
- Structure content according to the template format
- Generate appropriate technical documentation

## 🔄 How It Works

1. **Upload:** Submit your project folder path and documentation template
2. **Analysis:** The system analyzes your codebase using advanced LLM models
3. **Generation:** AI generates comprehensive documentation following your template structure
4. **Output:** Receive both Markdown and Jupyter Notebook versions
5. **Download:** Access your generated documentation files

## 📁 File Structure

```
Auto_Doc/
├── app.py                    # Main FastAPI application
├── utils.py                  # Utility functions for LLM integration
├── clarityforge_app/         # ClarityForge integration components
│   ├── handlers/            # Model, UI, Menu, and Preferences handlers
│   └── template_doc/        # Template storage and web uploads
├── temp/                    # Temporary file storage
├── output/                  # Generated documentation output
├── autodoc.log             # Application logs
└── README.md               # This file
```

## 🔍 Advanced Features

### Intelligent File Size Management
- Automatically handles large projects by progressively reducing file size limits
- Default: 100KB per file, 5MB total
- Fallback: 50KB per file, 2MB total
- Emergency: 20KB per file, 1MB total

### Error Handling
- Comprehensive error logging
- Automatic cleanup of temporary files
- Graceful handling of LLM response failures
- Progressive retry mechanisms for large projects

### Output Management
- Timestamped output directories
- Automatic filename sanitization
- Dual format generation (MD + IPYNB)
- Download link generation

## 🛠️ Dependencies

### Core Dependencies
- **FastAPI** - Modern, fast web framework for building APIs
- **uvicorn** - ASGI server for running FastAPI applications
- **nbformat** - Jupyter notebook format handling
- **python-multipart** - File upload handling
- **python-dotenv** - Environment variable management

### AI/LLM Integration
- **open_arena_lib** - Thomson Reuters OpenArena platform integration
- **requests** - HTTP client for authentication and API calls

### Development Tools
- **pathlib** - Modern path handling
- **logging** - Comprehensive logging system
- **datetime** - Timestamp generation
- **tempfile** - Secure temporary file handling

## 🐛 Troubleshooting

### Common Issues

**1. Authentication Errors**
- Verify your `.env` file configuration
- Check CLIENT_ID and CLIENT_SECRET values
- Ensure AUDIENCE matches your OpenArena setup

**2. Large Project Failures**
- The system automatically retries with smaller file size limits
- Check logs in `autodoc.log` for detailed error information
- Consider using a more specific template to guide the analysis

**3. Template Processing Issues**
- Ensure template file is in supported format (`.md`, `.txt`, `.ipynb`)
- For `.ipynb` templates, only markdown cells are processed
- Template should provide clear structure and guidance

### Logging
Check `autodoc.log` for detailed execution logs including:
- Request processing steps
- LLM communication details
- File operations
- Error stacktraces

## 📞 Support

For issues and questions:
1. Check the `autodoc.log` file for detailed error information
2. Verify your environment configuration
3. Review the FastAPI documentation at `http://localhost:5001/docs`
4. Contact the Responsible AI Hub team for OpenArena platform issues

---

**Part of the Thomson Reuters Responsible AI Hub (RAIH) Initiative**
