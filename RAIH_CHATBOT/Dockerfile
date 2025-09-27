# RAIH_CHATBOT Dockerfile
# RAI-Z - Intelligent Conversational AI with SQL Query Capabilities
# Part of Thomson Reuters Responsible AI Hub (RAIH)

# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Thomson Reuters Responsible AI Hub Team"
LABEL description="RAIH_CHATBOT - Intelligent Conversational AI with SQL Query Capabilities"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PORT=5000

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from parent directory
COPY ../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Additional dependencies for RAIH_CHATBOT specifically
RUN pip install --no-cache-dir \
    snowflake-connector-python>=3.6.0 \
    langchain-openai>=0.1.0 \
    cryptography>=41.0.0 \
    markdown>=3.4.0 \
    sqlalchemy>=2.0.0 \
    pandas>=2.0.0 \
    langchain>=0.1.0

# Create application user for security
RUN groupadd -r raihchatbot && useradd -r -g raihchatbot raihchatbot

# Create necessary directories with proper permissions
RUN mkdir -p /app/templates /app/logs /app/data && \
    chown -R raihchatbot:raihchatbot /app

# Copy the RAIH_CHATBOT application files
COPY --chown=raihchatbot:raihchatbot . .

# Ensure scripts are executable
RUN chmod +x app.py

# Create volume mounts for persistent data
VOLUME ["/app/logs", "/app/data"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/ || exit 1

# Switch to non-root user
USER raihchatbot

# Expose the port
EXPOSE $PORT

# Run the application
CMD ["python", "app.py"]