# Auto_Doc Dockerfile
# Automated Documentation Generator - Part of Responsible AI Hub (RAIH)

# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Thomson Reuters Responsible AI Hub Team"
LABEL description="Auto_Doc - Automated Documentation Generator API"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app" \
    PORT=5001

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements from parent directory
COPY ../requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Additional dependencies for Auto_Doc specifically
RUN pip install --no-cache-dir \
    nbformat>=5.9.0 \
    markdown>=3.4.0 \
    pathlib

# Create application user for security
RUN groupadd -r autodoc && useradd -r -g autodoc autodoc

# Create necessary directories with proper permissions
RUN mkdir -p /app/temp /app/output /app/clarityforge_app/template_doc/web_uploads /app/logs && \
    chown -R autodoc:autodoc /app

# Copy the Auto_Doc application files
COPY --chown=autodoc:autodoc . .

# Ensure scripts are executable
RUN chmod +x app.py

# Create volume mounts for persistent data
VOLUME ["/app/output", "/app/logs", "/app/temp"]

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# Switch to non-root user
USER autodoc

# Expose the port
EXPOSE $PORT

# Run the application
CMD ["python", "app.py"]