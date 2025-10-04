FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    poppler-utils \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libglib2.0-0 \
    libgtk-3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Download spacy model (optional - can be downloaded at runtime)
RUN python -c "import spacy; spacy.cli.download('en_core_web_sm')" || echo "Spacy model download failed - will use fallback"

# Copy application code
COPY . .

# Create necessary directories for cloud deployment
RUN mkdir -p /tmp/bionexus/uploads /tmp/bionexus/images /app/logs /app/data

# Expose port
EXPOSE 8000

# Set environment variables for cloud deployment
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV ENVIRONMENT=production
ENV CLOUD_ENVIRONMENT=gcp

# Health check for cloud services
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application with production settings
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]