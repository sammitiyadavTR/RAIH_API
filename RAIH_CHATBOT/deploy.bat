@echo off
REM RAIH_CHATBOT Docker Deployment Script for Windows
REM Part of Thomson Reuters Responsible AI Hub (RAIH)

echo 🤖 RAIH_CHATBOT (RAI-Z) Docker Deployment Script
echo ================================================

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo ⚠️  .env file not found. Creating from template...
    if exist .env.example (
        copy .env.example .env
        echo 📝 Please edit .env file with your actual configuration values.
        echo    Required configurations:
        echo    - Snowflake: SNOWFLAKE_USER, SNOWFLAKE_ACCOUNT, etc.
        echo    - OpenAI: OPENAI_WORKSPACE_ID, OPENAI_MODEL_NAME, etc.
        echo    - Thomson Reuters: TR_CLIENT_ID, TR_CLIENT_SECRET, etc.
        pause
    ) else (
        echo ❌ .env.example file not found. Please create .env file manually.
        pause
        exit /b 1
    )
)

echo 🏗️  Building RAIH_CHATBOT Docker image...
docker-compose build

echo 🚀 Starting RAIH_CHATBOT service...
docker-compose up -d

echo ⏳ Waiting for service to be ready...
timeout /t 15 /nobreak >nul

REM Check if service is running
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ RAIH_CHATBOT service is running!
    echo.
    echo 🌐 Service URLs:
    echo    Chat Interface: http://localhost:5000
    echo    API Docs: http://localhost:5000/docs
    echo    Health Check: http://localhost:5000/
    echo.
    echo 📊 Service Status:
    docker-compose ps
    echo.
    echo 💬 Test the Chatbot:
    echo    curl -X POST "http://localhost:5000/chatbot" -H "Content-Type: application/json" -d "{\"message\": \"ping\"}"
    echo.
    echo 📋 View Logs:
    echo    docker-compose logs -f raih-chatbot
    echo.
    echo 🛑 Stop Service:
    echo    docker-compose down
) else (
    echo ❌ Service failed to start properly. Checking logs...
    docker-compose logs raih-chatbot
    pause
    exit /b 1
)

pause