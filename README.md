# RAIH_API

**Responsible AI Hub (RAIH) - API Suite**

A collection of FastAPI-based services providing AI-powered solutions for documentation generation, data impact assessment, and intelligent conversational AI capabilities.

## 🚀 Overview

This repository contains three main APIs that support responsible AI practices and automation:

- **Auto_Doc** - Automated documentation generation from code repositories
- **DIA_Assistant** - Data Impact Assessment tool for evaluating data processing impacts
- **RAIH_CHATBOT** - Intelligent conversational AI with SQL query capabilities

## 📁 Project Structure

```
RAIH_API/
├── Auto_Doc/           # Documentation generation service (Port: 5001)
├── DIA_Assistant/      # Data Impact Assessment API (Port: 8000)
├── RAIH_CHATBOT/       # Conversational AI chatbot (Port: 5000)
├── requirements.txt    # Shared dependencies
└── README.md          # This file
```

## 🔧 Services

### 1. Auto_Doc - Documentation Generator
**Port:** `5001` | **Path:** `/Auto_Doc/`

Automatically generates comprehensive documentation from code repositories using AI analysis and customizable templates.

**Key Features:**
- 📝 AI-powered code analysis and documentation generation
- 🎯 Template-driven documentation structure
- 📊 Multiple output formats (Markdown & Jupyter Notebook)
- 🐳 Docker deployment ready

**Quick Start:**
```bash
cd Auto_Doc
docker-compose up -d
# Access: http://localhost:5001
```

[📖 Detailed Documentation](./Auto_Doc/README.md)

---

### 2. DIA_Assistant - Data Impact Assessment
**Port:** `8000` | **Path:** `/DIA_Assistant/`

AI-powered tool for conducting Data Impact Assessments (DIA) to evaluate data processing activities and their potential impacts.

**Key Features:**
- 📄 Multi-input support (file uploads & text scenarios)
- 🧠 AI-driven impact analysis using Thomson Reuters OpenArena
- 🌐 Interactive web interface for easy testing
- 🔒 Secure file handling with automated cleanup

**Quick Start:**
```bash
cd DIA_Assistant
docker-compose up -d
# Access: http://localhost:8000
```

[📖 Detailed Documentation](./DIA_Assistant/README.md)

---

### 3. RAIH_CHATBOT - Conversational AI
**Port:** `5000` | **Path:** `/RAIH_CHATBOT/`

Intelligent chatbot (RAI-Z) that combines natural language processing with database querying capabilities for smart query routing.

**Key Features:**
- 🤖 Intelligent query classification and routing
- 🗃️ SQL database integration with natural language queries
- 💬 General conversational AI capabilities
- 🎯 Confidence-based response routing

**Quick Start:**
```bash
cd RAIH_CHATBOT
docker-compose up -d
# Access: http://localhost:5000
```

[📖 Detailed Documentation](./RAIH_CHATBOT/README.md)

## 🚀 Quick Start - All Services

### Prerequisites
- Docker and Docker Compose
- Valid Thomson Reuters OpenArena credentials

### Deploy All Services
```bash
# Clone the repository
git clone https://github.com/sammitiyadavTR/RAIH_API.git
cd RAIH_API

# Configure each service (copy and edit .env files)
cp Auto_Doc/.env.example Auto_Doc/.env
cp DIA_Assistant/.env.example DIA_Assistant/.env
cp RAIH_CHATBOT/.env.example RAIH_CHATBOT/.env

# Deploy services individually
cd Auto_Doc && docker-compose up -d && cd ..
cd DIA_Assistant && docker-compose up -d && cd ..
cd RAIH_CHATBOT && docker-compose up -d && cd ..
```

### Service URLs
- **Auto_Doc:** [http://localhost:5001](http://localhost:5001)
- **DIA_Assistant:** [http://localhost:8000](http://localhost:8000) 
- **RAIH_CHATBOT:** [http://localhost:5000](http://localhost:5000)

## 🛠️ Technology Stack

- **FastAPI** - Modern, fast web framework for building APIs
- **uvicorn** - ASGI server for production deployments
- **Docker** - Containerization for consistent deployments
- **Thomson Reuters OpenArena** - AI/LLM platform integration
- **Python 3.11** - Core programming language

## 📚 API Documentation

Each service provides interactive API documentation:
- **Auto_Doc:** [http://localhost:5001/docs](http://localhost:5001/docs)
- **DIA_Assistant:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **RAIH_CHATBOT:** [http://localhost:5000/docs](http://localhost:5000/docs)

## 🏷️ Abbreviations

- **RAIH** - Responsible AI Hub
- **RAI** - Responsible AI
- **DIA** - Data Impact Assessment
- **RAI-Z** - Responsible AI Chatbot (RAIH_CHATBOT service name)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is part of the Thomson Reuters Responsible AI Hub initiative.

---

**Built with ❤️ by the Thomson Reuters Responsible AI Hub Team**
