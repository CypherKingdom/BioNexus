#!/bin/bash

# BioNexus Frontend Setup Script
# This script installs all required dependencies and sets up the development environment

set -e

echo "🚀 Setting up BioNexus Frontend..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
  echo "❌ Error: package.json not found. Please run this script from the frontend directory."
  exit 1
fi

# Check for package manager preference
if command -v pnpm &> /dev/null; then
  PACKAGE_MANAGER="pnpm"
elif command -v yarn &> /dev/null; then
  PACKAGE_MANAGER="yarn"
else
  PACKAGE_MANAGER="npm"
fi

echo "📦 Using package manager: $PACKAGE_MANAGER"

# Clean any existing installations
echo "🧹 Cleaning previous installations..."
rm -rf node_modules
rm -f package-lock.json yarn.lock pnpm-lock.yaml

# Install dependencies
echo "📦 Installing dependencies..."
case $PACKAGE_MANAGER in
  "pnpm")
    pnpm install
    ;;
  "yarn")
    yarn install
    ;;
  *)
    npm install
    ;;
esac

# Create .env.local if it doesn't exist
if [ ! -f ".env.local" ]; then
  echo "⚙️ Creating .env.local from template..."
  cp .env.example .env.local
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p .next
mkdir -p public/images
mkdir -p public/icons

# Type check
echo "🔍 Running type check..."
case $PACKAGE_MANAGER in
  "pnpm")
    pnpm run type-check || echo "⚠️ Type check found issues, but continuing..."
    ;;
  "yarn")
    yarn type-check || echo "⚠️ Type check found issues, but continuing..."
    ;;
  *)
    npm run type-check || echo "⚠️ Type check found issues, but continuing..."
    ;;
esac

echo "✅ Frontend setup complete!"
echo ""
echo "To start the development server:"
echo "  $PACKAGE_MANAGER run dev"
echo ""
echo "To build for production:"
echo "  $PACKAGE_MANAGER run build"
echo ""
echo "The application will be available at: http://localhost:3000"