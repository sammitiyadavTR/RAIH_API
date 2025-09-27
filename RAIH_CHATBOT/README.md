# RAIH_CHATBOT

**RAI-Z - Intelligent Conversational AI with SQL Query Capabilities**  
*Part of Thomson Reuters Responsible AI Hub (RAIH)*

A sophisticated FastAPI-based chatbot that combines natural language processing with database querying capabilities. The system intelligently routes user queries between SQL database operations and general conversational AI using advanced query classification.

## 🚀 Overview

RAIH_CHATBOT (RAI-Z) is an intelligent conversational AI system that can:
- Process natural language queries and determine the appropriate response strategy
- Execute SQL queries against Snowflake databases for data retrieval
- Provide general conversational AI responses using Thomson Reuters OpenArena platform
- Route queries intelligently based on content analysis and confidence scoring
- Deliver responses in a user-friendly web interface

## ✨ Key Features

- 🧠 **Intelligent Query Routing** - Automatically classifies queries as SQL or conversational
- 🗃️ **SQL Database Integration** - Direct querying of Snowflake databases with natural language
- 💬 **Conversational AI** - General chat capabilities using advanced LLM models
- 🎯 **Confidence-based Routing** - Smart routing based on query confidence scores
- 🌐 **Web Interface** - Clean, responsive web UI for easy interaction
- 📊 **Debug Information** - Detailed execution info for troubleshooting
- 🔒 **Secure Authentication** - Multiple authentication methods for different services
- ⚡ **Real-time Processing** - Fast response times with efficient query handling

## 🏗️ Architecture

### Core Components

1. **SimpleRouterAgent** (`OpenArena_ChatbotChain.py`)
   - Query classification engine
   - Routes queries to appropriate agents
   - Confidence threshold management
   - Response formatting and processing

2. **SQL Agent** (`SQLAgent.py`)
   - Snowflake database connectivity
   - Natural language to SQL conversion
   - Query execution and result formatting
   - Database schema awareness

3. **FastAPI Application** (`app.py`)
   - REST API endpoints
   - Request/response handling
   - Error management and logging
   - Web interface serving

4. **Web Interface** (`templates/index.html`)
   - Responsive chat interface
   - Real-time message handling
   - Debug information display
   - Modern UI with gradient themes

## 🔧 API Endpoints

### 1. Root Endpoint
```http
GET /
```
**Description:** Health check endpoint to verify API status

**Response:**
```json
{
  "status": "success",
  "message": "FastAPI server is running"
}
```

### 2. Chatbot Endpoint
```http
POST /chatbot
```
**Description:** Main chatbot interface for processing user queries

**Request Body:**
```json
{
  "message": "Your query here"
}
```

**Success Response:**
```json
{
  "status": "success",
  "message": "<formatted_html_response>",
  "debug_info": {
    "agent_used": "sql_agent|rag_agent",
    "classification": "sql|rag|ambiguous",
    "execution_time": 1.23
  }
}
```

**Error Response:**
```json
{
  "status": "error",
  "message": "Error description",
  "debug_info": {}
}
```

### 3. Web Interface
```http
GET /templates/index.html
```
**Description:** Serves the web-based chat interface

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- Access to Snowflake database
- Thomson Reuters OpenArena platform access
- Valid authentication credentials for all services

## 🐳 Docker Deployment (Recommended)

### Quick Start with Docker

1. **Navigate to RAIH_CHATBOT directory:**
   ```bash
   cd RAIH_CHATBOT
   ```

2. **Configure environment variables:**
   ```bash
   # Copy the example environment file
   cp .env.example .env
   
   # Edit .env with your actual values
   ```

3. **Deploy with Docker Compose:**
   ```bash
   # Build and start the service
   docker-compose up -d
   
   # Check service status
   docker-compose ps
   
   # View logs
   docker-compose logs -f raih-chatbot
   
   # Stop the service
   docker-compose down
   ```

The chatbot will be available at `http://localhost:5000`

### Docker Features
- ✅ **Isolated Environment** - Secure container deployment
- ✅ **Persistent Storage** - Volume mounts for logs and data
- ✅ **Health Monitoring** - Built-in health checks
- ✅ **Auto Restart** - Automatic service recovery
- ✅ **Resource Management** - CPU and memory limits

## 🐍 Local Python Installation (Alternative)

### Installation Steps

1. **Navigate to RAIH_CHATBOT directory:**
   ```bash
   cd RAIH_CHATBOT
   ```

2. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   pip install snowflake-connector-python
   pip install langchain-openai
   pip install cryptography
   pip install markdown
   ```

3. **Configure environment variables:**
   Create a `.env` file with the following variables:

   ```env
   # Snowflake Database Configuration
   SNOWFLAKE_USER=your_snowflake_user
   SNOWFLAKE_ACCOUNT=your_account.region
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_DATABASE=your_database
   SNOWFLAKE_SCHEMA=your_schema
   SNOWFLAKE_ROLE=your_role
   SNOWFLAKE_PRIVATE_KEY=your_private_key
   PRIVATE_KEY_PASSPHRASE=your_passphrase
   DB_ALLOWED_TABLES=table1,table2,table3

   # OpenAI/Azure Configuration
   OPENAI_WORKSPACE_ID=your_workspace_id
   OPENAI_MODEL_NAME=your_model_name
   OPENAI_ASSET_ID=your_asset_id
   OPENAI_BASE_URL=your_base_url

   # Thomson Reuters OpenArena
   TR_CLIENT_ID=your_client_id
   TR_CLIENT_SECRET=your_client_secret
   TR_AUDIENCE=your_audience
   TR_TOKEN_URL=your_token_url
   OPEN_ARENA_WORKFLOW_ID=your_workflow_id
   OPEN_ARENA_API_VERSION=your_api_version
   OPEN_ARENA_BASE_URL=your_base_url

   # Default Authentication
   DEFAULT_AUTH_TOKEN=your_default_token
   ```

4. **Run the application:**
   ```bash
   python app.py
   ```

The chatbot will be available at `http://localhost:5000`

## 🎯 Usage Examples

### SQL Queries
```
"Show me all users from the database"
"What's the total sales for last month?"
"List the top 10 products by revenue"
"Find customers in New York"
```

### Conversational Queries
```
"What is machine learning?"
"Explain the concept of responsible AI"
"How does natural language processing work?"
"What are the latest trends in AI?"
```

### Ping Test
```
"ping" → Returns server status
```

## 🔄 Query Routing Logic

The system uses intelligent routing based on:

1. **Keyword Analysis** - Identifies SQL-related terms and operations
2. **Database Schema Awareness** - Recognizes table and column references
3. **Confidence Scoring** - Assigns confidence scores to different interpretations
4. **Threshold-based Routing** - Routes to SQL agent if confidence > 0.36
5. **Fallback Handling** - Defaults to conversational AI for ambiguous queries

## 📁 File Structure

```
RAIH_CHATBOT/
├── app.py                          # Main FastAPI application
├── OpenArena_ChatbotChain.py       # Query routing and classification
├── SQLAgent.py                     # Database connectivity and SQL operations
├── templates/
│   └── index.html                  # Web interface
├── .env                           # Environment configuration
├── .env.example                   # Environment template
├── Dockerfile                     # Docker container definition
├── docker-compose.yml             # Docker Compose configuration
├── .dockerignore                  # Docker ignore rules
└── README.md                      # This file
```

## 🔍 Advanced Features

### Query Classification
- **Multi-strategy classification** using keyword analysis and schema matching
- **Confidence scoring** for routing decisions
- **Fallback mechanisms** for ambiguous queries
- **Debug information** for transparency

### SQL Agent Capabilities
- **Natural language to SQL** conversion
- **Schema-aware querying** with table and column validation
- **Result formatting** for user-friendly display
- **Error handling** with meaningful messages

### Security Features
- **Environment-based configuration** for sensitive credentials
- **Private key authentication** for Snowflake
- **Token-based authentication** for external services
- **Query validation** and sanitization

## 🛠️ Dependencies

### Core Dependencies
- **FastAPI** - Modern web framework for APIs
- **uvicorn** - ASGI server for running FastAPI
- **pydantic** - Data validation and parsing
- **python-dotenv** - Environment variable management

### AI/ML Libraries
- **langchain-openai** - LangChain integration with OpenAI
- **open_arena_lib** - Thomson Reuters OpenArena platform integration

### Database Libraries
- **snowflake-connector-python** - Snowflake database connectivity
- **sqlalchemy** - SQL toolkit and ORM
- **pandas** - Data manipulation and analysis

### Utility Libraries
- **cryptography** - Cryptographic operations for secure authentication
- **markdown** - Markdown to HTML conversion
- **requests** - HTTP client library

## 🐛 Troubleshooting

### Common Issues

**1. Database Connection Errors**
- Verify Snowflake credentials in `.env` file
- Check network connectivity to Snowflake
- Validate private key format and passphrase

**2. Authentication Failures**
- Confirm Thomson Reuters OpenArena credentials
- Check token expiration and refresh mechanisms
- Verify audience and client ID configuration

**3. Query Routing Issues**
- Check confidence threshold (default: 0.36)
- Review query classification in debug info
- Validate database schema and table permissions

**4. Web Interface Problems**
- Ensure FastAPI server is running on port 5000
- Check browser console for JavaScript errors
- Verify template file accessibility

### Debug Information
The chatbot provides detailed debug information including:
- **Agent Used** - Which agent processed the query
- **Classification** - Query type classification result
- **Execution Time** - Processing time in seconds
- **Error Details** - Specific error messages and stack traces

## 📞 Support

For issues and questions:
1. Check the application logs for detailed error information
2. Verify environment configuration and credentials
3. Review the FastAPI documentation at `http://localhost:5000/docs`
4. Contact the Responsible AI Hub team for platform-specific issues

## 📈 Performance Considerations

- **Connection Pooling** - Efficient database connection management
- **Query Caching** - Results caching for frequently accessed data
- **Async Processing** - Non-blocking request handling
- **Resource Limits** - Configurable CPU and memory constraints
- **Timeout Management** - Request timeout handling

---

**Part of the Thomson Reuters Responsible AI Hub (RAIH) Initiative**  
*Building responsible AI solutions for the future*