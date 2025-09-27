#!/bin/bash

# DIA_Assistant Docker Deployment Script
# Part of Thomson Reuters Responsible AI Hub (RAIH)

set -e

echo "📊 DIA_Assistant Docker Deployment Script"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating from template..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "📝 Please edit .env file with your actual configuration values."
        echo "   Required: CLIENT_ID, CLIENT_SECRET, AUDIENCE"
        echo "   Optional: PERSONAL_TOKEN, WORKFLOW_ID"
        read -p "Press Enter to continue after editing .env file..."
    else
        echo "❌ .env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

echo "🏗️  Building DIA_Assistant Docker image..."
docker-compose build

echo "🚀 Starting DIA_Assistant service..."
docker-compose up -d

echo "⏳ Waiting for service to be ready..."
sleep 10

# Check if service is healthy
if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ DIA_Assistant service is running and healthy!"
    echo ""
    echo "🌐 Service URLs:"
    echo "   Web Interface: http://localhost:8000"
    echo "   API Docs: http://localhost:8000/docs"
    echo "   API Status: http://localhost:8000/api/status"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "🧪 Test the API:"
    echo "   curl -X POST 'http://localhost:8000/analyze-text' -H 'Content-Type: application/json' -d '{\"text_input\": \"Test analysis\"}'"
    echo ""
    echo "📋 View Logs:"
    echo "   docker-compose logs -f dia-assistant"
    echo ""
    echo "🛑 Stop Service:"
    echo "   docker-compose down"
elif docker-compose ps | grep -q "Up"; then
    echo "⚠️  Service is running but may not be fully ready yet. Checking logs..."
    docker-compose logs --tail=20 dia-assistant
    echo ""
    echo "🌐 Service should be available at: http://localhost:8000"
else
    echo "❌ Service failed to start properly. Checking logs..."
    docker-compose logs dia-assistant
    exit 1
fi