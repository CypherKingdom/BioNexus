# BioNexus Development Guide

This guide ensures consistent development setup across Windows, macOS, and Linux.

## 📋 Prerequisites

### Required Software (All Platforms)

1. **Docker & Docker Compose**
   - **Windows**: Docker Desktop for Windows
   - **macOS**: Docker Desktop for Mac
   - **Linux**: Docker CE + Docker Compose

2. **Node.js 18+**
   - Download from [nodejs.org](https://nodejs.org/)
   - Verify: `node --version` (should be 18.0.0+)

3. **Python 3.10+**
   - **Windows**: Download from python.org or use Microsoft Store
   - **macOS**: Use Homebrew (`brew install python@3.10`) or python.org
   - **Linux**: Use package manager (`apt install python3.10` or `dnf install python3.10`)
   - Verify: `python3 --version` (should be 3.10.0+)

4. **Git**
   - Pre-installed on macOS/Linux
   - **Windows**: Download from git-scm.com

### Optional but Recommended

- **Package Managers**:
  - **Windows**: Chocolatey or Scoop
  - **macOS**: Homebrew
  - **Linux**: Built-in package managers

- **Node Package Manager**: pnpm (faster than npm)
  ```bash
  npm install -g pnpm
  ```

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <repository-url>
cd bionexus
```

### 2. Automated Setup
```bash
# Make setup script executable (Linux/macOS)
chmod +x setup.sh

# Run setup script (all platforms)
./setup.sh
```

### 3. Manual Setup (if automated fails)

#### Backend Setup
```bash
cd backend

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# Windows (Command Prompt)
venv\Scripts\activate
# Windows (PowerShell)
venv\Scripts\Activate.ps1
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Create environment file
cp ../.env.example .env
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install
# OR with pnpm (recommended)
pnpm install

# Create environment file
cp .env.example .env.local
```

## ⚙️ Configuration

### Environment Variables

Create and customize these files:
- **Root**: `.env` (main configuration)
- **Frontend**: `frontend/.env.local`
- **Backend**: `backend/.env` (optional, inherits from root)

### Key Configuration Options

```bash
# Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# API Endpoints
API_BASE_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

# Development
DEBUG=true
LOG_LEVEL=INFO
```

## 🏃‍♂️ Running the Application

### Option 1: Docker (Recommended)
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Manual Development Servers

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # Linux/macOS
# OR venv\Scripts\activate  # Windows
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
# OR pnpm dev
```

### Option 3: Using Makefile (Linux/macOS)
```bash
make setup    # Initial setup
make dev      # Start development servers
make test     # Run tests
make health   # Check service health
```

## 🌐 Access Points

Once running, access these URLs:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474

## 🧪 Testing

### Backend Tests
```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Start services first
docker-compose up -d

# Run integration tests
cd backend
pytest tests/integration/ -v
```

## 🔧 Troubleshooting

### Common Issues

#### Port Conflicts
If ports 3000, 7474, 7687, or 8000 are in use:

1. **Find process using port**:
   ```bash
   # Windows
   netstat -ano | findstr :8000
   # macOS/Linux
   lsof -i :8000
   ```

2. **Kill process or change ports** in docker-compose.yml

#### Permission Errors (Windows)
- Run terminal as Administrator
- Ensure Docker Desktop has proper permissions
- Check Windows Subsystem for Linux (WSL2) if using it

#### Module Not Found Errors
```bash
# Reinstall dependencies
cd backend && pip install -r requirements.txt
cd frontend && rm -rf node_modules && npm install
```

#### Docker Issues
```bash
# Reset Docker
docker system prune -af
docker-compose down -v
docker-compose up -d --build
```

### Platform-Specific Issues

#### Windows
- **PowerShell Execution Policy**: Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`
- **Long Path Support**: Enable in Windows settings or use WSL2
- **Antivirus**: Exclude project directory from real-time scanning

#### macOS
- **Xcode Command Line Tools**: `xcode-select --install`
- **Permission Issues**: Use `sudo` only when necessary
- **M1/M2 Compatibility**: Some Docker images may need ARM64 variants

#### Linux
- **Docker Permissions**: Add user to docker group: `sudo usermod -aG docker $USER`
- **System Dependencies**: Install tesseract, poppler-utils via package manager
- **Python Development Headers**: Install python3-dev package

## 🔄 Development Workflow

### Daily Development
1. **Pull latest changes**: `git pull origin main`
2. **Start services**: `docker-compose up -d`
3. **Check health**: `curl http://localhost:8000/health`
4. **Development**: Edit code with hot reload enabled
5. **Test changes**: Run relevant test suites
6. **Commit**: Follow conventional commit format

### Adding New Features
1. **Create feature branch**: `git checkout -b feature/feature-name`
2. **Develop feature** with tests
3. **Run full test suite**: `make test`
4. **Update documentation** if needed
5. **Create pull request**

### Database Changes
1. **Backup current data**: `make backup`
2. **Update Cypher scripts** in `infra/`
3. **Test migration** on development data
4. **Document changes** in migration notes

## 📚 Additional Resources

- **API Documentation**: Available at `/docs` when backend is running
- **Database Schema**: See `infra/cypher_setup.cypher`
- **Docker Logs**: `docker-compose logs [service-name]`
- **Performance Monitoring**: Built-in metrics at `/metrics`

## 🤝 Contributing

1. **Fork repository**
2. **Create feature branch**
3. **Follow coding standards**:
   - **Python**: Black formatting, PEP 8 compliance
   - **TypeScript**: Prettier + ESLint rules
4. **Add tests** for new features
5. **Update documentation**
6. **Submit pull request**

## 🆘 Getting Help

1. **Check logs** for error messages
2. **Review documentation** in `/docs`
3. **Search existing issues** on GitHub
4. **Create detailed issue** with:
   - Operating system and version
   - Error messages and logs
   - Steps to reproduce
   - Expected vs actual behavior

---

**Happy coding! 🚀**