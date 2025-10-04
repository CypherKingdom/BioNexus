# BioNexus Project Makefile
# Cross-platform project management commands

.PHONY: help setup install clean build test lint format dev start stop restart logs status health demo

# Default target
help:
	@echo "BioNexus Project Commands"
	@echo "========================="
	@echo ""
	@echo "Setup Commands:"
	@echo "  setup         - Initial project setup (install dependencies, create env files)"
	@echo "  install       - Install all dependencies"
	@echo "  clean         - Clean build artifacts and cache files"
	@echo ""
	@echo "Development Commands:"
	@echo "  dev           - Start development servers"
	@echo "  build         - Build the project"
	@echo "  test          - Run all tests"
	@echo "  lint          - Run linting checks"
	@echo "  format        - Format code"
	@echo ""
	@echo "Docker Commands:"
	@echo "  start         - Start Docker services"
	@echo "  stop          - Stop Docker services"
	@echo "  restart       - Restart Docker services"
	@echo "  logs          - View Docker logs"
	@echo "  status        - Check service status"
	@echo ""
	@echo "Application Commands:"
	@echo "  health        - Check application health"
	@echo "  demo          - Run demo workflow"
	@echo ""

# Setup
setup:
	@echo "🚀 Setting up BioNexus project..."
	./setup.sh

install: install-backend install-frontend

install-backend:
	@echo "📦 Installing backend dependencies..."
	cd backend && ./setup.sh

install-frontend:
	@echo "📦 Installing frontend dependencies..."
	cd frontend && ./setup.sh

# Clean
clean: clean-backend clean-frontend clean-docker
	@echo "🧹 Cleaning project..."

clean-backend:
	@echo "🧹 Cleaning backend..."
	cd backend && rm -rf __pycache__ .pytest_cache .coverage htmlcov dist build *.egg-info
	cd backend && find . -type d -name "__pycache__" -exec rm -rf {} + || true

clean-frontend:
	@echo "🧹 Cleaning frontend..."
	cd frontend && rm -rf .next out dist node_modules/.cache

clean-docker:
	@echo "🧹 Cleaning Docker..."
	docker system prune -f || true

# Development
dev: dev-backend dev-frontend

dev-backend:
	@echo "🐍 Starting backend development server..."
	cd backend && source venv/bin/activate && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev-frontend:
	@echo "⚛️ Starting frontend development server..."
	cd frontend && npm run dev

# Build
build: build-backend build-frontend

build-backend:
	@echo "🔨 Building backend..."
	cd backend && source venv/bin/activate && python -m pytest --cov=app

build-frontend:
	@echo "🔨 Building frontend..."
	cd frontend && npm run build

# Testing
test: test-backend test-frontend

test-backend:
	@echo "🧪 Running backend tests..."
	cd backend && source venv/bin/activate && python -m pytest tests/ -v --cov=app --cov-report=html

test-frontend:
	@echo "🧪 Running frontend tests..."
	cd frontend && npm test

# Linting
lint: lint-backend lint-frontend

lint-backend:
	@echo "🔍 Linting backend..."
	cd backend && source venv/bin/activate && flake8 app/ tests/ --max-line-length=100
	cd backend && source venv/bin/activate && black --check app/ tests/
	cd backend && source venv/bin/activate && isort --check-only app/ tests/

lint-frontend:
	@echo "🔍 Linting frontend..."
	cd frontend && npm run lint

# Formatting
format: format-backend format-frontend

format-backend:
	@echo "✨ Formatting backend code..."
	cd backend && source venv/bin/activate && black app/ tests/
	cd backend && source venv/bin/activate && isort app/ tests/

format-frontend:
	@echo "✨ Formatting frontend code..."
	cd frontend && npm run format || npx prettier --write "**/*.{js,jsx,ts,tsx,json,css,md}"

# Docker Management
start:
	@echo "🐳 Starting Docker services..."
	docker-compose up -d

stop:
	@echo "🛑 Stopping Docker services..."
	docker-compose down

restart:
	@echo "🔄 Restarting Docker services..."
	docker-compose restart

logs:
	@echo "📋 Showing Docker logs..."
	docker-compose logs -f

status:
	@echo "📊 Checking service status..."
	docker-compose ps

# Health checks
health:
	@echo "🏥 Checking application health..."
	@echo "Backend API:" && curl -f http://localhost:8000/health || echo "❌ Backend not responding"
	@echo "Frontend:" && curl -f http://localhost:3000 || echo "❌ Frontend not responding"
	@echo "Neo4j:" && curl -f http://localhost:7474 || echo "❌ Neo4j not responding"

# Demo
demo:
	@echo "🎬 Running BioNexus demo..."
	./scripts/run_demo.sh

# Database operations
db-setup:
	@echo "🗄️ Setting up database..."
	docker-compose exec neo4j cypher-shell -u neo4j -p password -f /setup/cypher_setup.cypher

db-reset:
	@echo "🔄 Resetting database..."
	docker-compose exec neo4j cypher-shell -u neo4j -p password -c "MATCH (n) DETACH DELETE n"

# Utility commands
backup:
	@echo "💾 Creating backup..."
	mkdir -p backups
	docker-compose exec neo4j neo4j-admin dump --database=neo4j --to=/var/lib/neo4j/backups/backup-$(shell date +%Y%m%d-%H%M%S).dump

docs:
	@echo "📚 Opening documentation..."
	@echo "API Documentation: http://localhost:8000/docs"
	@echo "Project README: README.md"
	@echo "Demo Guide: DEMO.md"

# Production deployment
deploy-prod:
	@echo "🚀 Deploying to production..."
	docker-compose -f docker-compose.prod.yml up -d

# Environment setup
env-setup:
	@echo "⚙️ Setting up environment files..."
	[ -f .env ] || cp .env.example .env
	[ -f frontend/.env.local ] || cp frontend/.env.example frontend/.env.local
	[ -f backend/.env ] || cp .env.example backend/.env