#!/bin/bash

# BioNexus Backend Setup Script
# This script sets up the Python environment and installs all required dependencies

set -e

echo "🚀 Setting up BioNexus Backend..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
  echo "❌ Error: requirements.txt not found. Please run this script from the backend directory."
  exit 1
fi

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
required_version="3.10"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
  echo "❌ Error: Python 3.10+ is required. Found: $python_version"
  exit 1
fi

echo "✅ Python version: $python_version"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "📦 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install system dependencies (for OCR and image processing)
echo "🔧 Installing system dependencies..."
if command -v apt-get &> /dev/null; then
  sudo apt-get update
  sudo apt-get install -y tesseract-ocr tesseract-ocr-eng poppler-utils
elif command -v yum &> /dev/null; then
  sudo yum install -y tesseract tesseract-langpack-eng poppler-utils
elif command -v dnf &> /dev/null; then
  sudo dnf install -y tesseract tesseract-langpack-eng poppler-utils
elif command -v brew &> /dev/null; then
  brew install tesseract poppler
else
  echo "⚠️ Could not detect package manager. Please install tesseract and poppler manually."
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Download spaCy model
echo "📖 Downloading spaCy biomedical model..."
python -m spacy download en_core_web_sm || echo "⚠️ Could not download en_core_web_sm"

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p data/uploads
mkdir -p data/processed
mkdir -p data/embeddings
mkdir -p data/exports
mkdir -p logs

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
  echo "⚙️ Creating .env from template..."
  cp ../.env.example .env
fi

# Test imports
echo "🔍 Testing key imports..."
python -c "
try:
    import fastapi
    import neo4j
    import pytesseract
    import pdf2image
    import transformers
    print('✅ All key packages imported successfully')
except ImportError as e:
    print(f'⚠️ Import error: {e}')
"

echo "✅ Backend setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "The API will be available at: http://localhost:8000"
echo "API Documentation: http://localhost:8000/docs"