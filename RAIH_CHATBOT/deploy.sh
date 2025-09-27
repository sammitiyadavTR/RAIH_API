#!/bin/bash

# RAIH_CHATBOT Docker Deployment Script
# Part of Thomson Reuters Responsible AI Hub (RAIH)

set -e

echo "🤖 RAIH_CHATBOT (RAI-Z) Docker Deployment Script"
echo "================================================"

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
        echo "   Required configurations:"
        echo "   - Snowflake: SNOWFLAKE_USER, SNOWFLAKE_ACCOUNT, etc."
        echo "   - OpenAI: OPENAI_WORKSPACE_ID, OPENAI_MODEL_NAME, etc."
        echo "   - Thomson Reuters: TR_CLIENT_ID, TR_CLIENT_SECRET, etc."
        read -p "Press Enter to continue after editing .env file..."
    else
        echo "❌ .env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

echo "🏗️  Building RAIH_CHATBOT Docker image..."
docker-compose build

echo "🚀 Starting RAIH_CHATBOT service..."
docker-compose up -d

echo "⏳ Waiting for service to be ready..."
sleep 15

# Check if service is healthy
if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ RAIH_CHATBOT service is running and healthy!"
    echo ""
    echo "🌐 Service URLs:"
    echo "   Chat Interface: http://localhost:5000"
    echo "   API Docs: http://localhost:5000/docs"
    echo "   Health Check: http://localhost:5000/"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "💬 Test the Chatbot:"
    echo "   curl -X POST 'http://localhost:5000/chatbot' -H 'Content-Type: application/json' -d '{\"message\": \"ping\"}'"
    echo ""
    echo "📋 View Logs:"
    echo "   docker-compose logs -f raih-chatbot"
    echo ""
    echo "🛑 Stop Service:"
    echo "   docker-compose down"
elif docker-compose ps | grep -q "Up"; then
    echo "⚠️  Service is running but may not be fully ready yet. Checking logs..."
    docker-compose logs --tail=20 raih-chatbot
    echo ""
    echo "🌐 Service should be available at: http://localhost:5000"
else
    echo "❌ Service failed to start properly. Checking logs..."
    docker-compose logs raih-chatbot
    exit 1
fi