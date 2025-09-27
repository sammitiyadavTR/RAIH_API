@echo off
REM Auto_Doc Docker Deployment Script for Windows
REM Part of Thomson Reuters Responsible AI Hub (RAIH)

echo 🚀 Auto_Doc Docker Deployment Script
echo ====================================

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
        echo    Required: CLIENT_ID, CLIENT_SECRET, AUDIENCE
        pause
    ) else (
        echo ❌ .env.example file not found. Please create .env file manually.
        pause
        exit /b 1
    )
)

echo 🏗️  Building Auto_Doc Docker image...
docker-compose build

echo 🚀 Starting Auto_Doc service...
docker-compose up -d

echo ⏳ Waiting for service to be ready...
timeout /t 10 /nobreak >nul

REM Check if service is running
docker-compose ps | findstr "Up" >nul
if %errorlevel% equ 0 (
    echo ✅ Auto_Doc service is running!
    echo.
    echo 🌐 Service URLs:
    echo    API: http://localhost:5001
    echo    Docs: http://localhost:5001/docs
    echo    Health: http://localhost:5001/health
    echo.
    echo 📊 Service Status:
    docker-compose ps
    echo.
    echo 📋 View Logs:
    echo    docker-compose logs -f autodoc
    echo.
    echo 🛑 Stop Service:
    echo    docker-compose down
) else (
    echo ❌ Service failed to start properly. Checking logs...
    docker-compose logs autodoc
    pause
    exit /b 1
)

pause