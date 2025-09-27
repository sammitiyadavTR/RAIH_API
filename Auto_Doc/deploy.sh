#!/bin/bash

# Auto_Doc Docker Deployment Script
# Part of Thomson Reuters Responsible AI Hub (RAIH)

set -e

echo "🚀 Auto_Doc Docker Deployment Script"
echo "===================================="

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
        read -p "Press Enter to continue after editing .env file..."
    else
        echo "❌ .env.example file not found. Please create .env file manually."
        exit 1
    fi
fi

echo "🏗️  Building Auto_Doc Docker image..."
docker-compose build

echo "🚀 Starting Auto_Doc service..."
docker-compose up -d

echo "⏳ Waiting for service to be ready..."
sleep 10

# Check if service is healthy
if docker-compose ps | grep -q "Up (healthy)"; then
    echo "✅ Auto_Doc service is running and healthy!"
    echo ""
    echo "🌐 Service URLs:"
    echo "   API: http://localhost:5001"
    echo "   Docs: http://localhost:5001/docs"
    echo "   Health: http://localhost:5001/health"
    echo ""
    echo "📊 Service Status:"
    docker-compose ps
    echo ""
    echo "📋 View Logs:"
    echo "   docker-compose logs -f autodoc"
    echo ""
    echo "🛑 Stop Service:"
    echo "   docker-compose down"
else
    echo "❌ Service failed to start properly. Checking logs..."
    docker-compose logs autodoc
    exit 1
fi