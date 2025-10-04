#!/bin/bash

# BioNexus Project Validation Script
# Validates project setup, dependencies, and configuration across platforms

echo "🔍 BioNexus Project Validation"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validation counters
TESTS_PASSED=0
TESTS_FAILED=0

# Helper functions
pass_test() {
    echo -e "${GREEN}✅ $1${NC}"
    ((TESTS_PASSED++))
}

fail_test() {
    echo -e "${RED}❌ $1${NC}"
    ((TESTS_FAILED++))
}

warn_test() {
    echo -e "${YELLOW}⚠️ $1${NC}"
}

info_test() {
    echo -e "${BLUE}ℹ️ $1${NC}"
}

# Check if we're in the project root
if [ ! -f "docker-compose.yml" ]; then
    fail_test "Not in BioNexus project root (docker-compose.yml not found)"
    exit 1
fi

pass_test "Project structure validation"

echo ""
echo "🔧 Checking System Dependencies..."

# Check required tools
check_command() {
    if command -v $1 &> /dev/null; then
        pass_test "$1 is available"
        return 0
    else
        fail_test "$1 is not installed"
        return 1
    fi
}

# Check Docker (optional)
DOCKER_AVAILABLE=false
if command -v docker &> /dev/null; then
    pass_test "docker is available"
    if command -v docker-compose &> /dev/null; then
        pass_test "docker-compose is available"
        DOCKER_AVAILABLE=true
    else
        fail_test "docker-compose is not installed"
    fi
else
    fail_test "docker is not installed"
fi

# Check required tools
check_command "python3" || true
check_command "node" || true
check_command "npm" || true

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+' | head -1)
if [ "$(printf '%s\n' "3.10" "$python_version" | sort -V | head -n1)" = "3.10" ]; then
    pass_test "Python version $python_version (>= 3.10)"
else
    fail_test "Python version $python_version (requires >= 3.10)"
fi

# Check Node version
node_version=$(node --version | grep -oE '[0-9]+\.[0-9]+' | head -1)
if [ "$(printf '%s\n' "18.0" "$node_version" | sort -V | head -n1)" = "18.0" ]; then
    pass_test "Node.js version $node_version (>= 18.0)"
else
    fail_test "Node.js version $node_version (requires >= 18.0)"
fi

echo ""
echo "📁 Checking Project Structure..."

# Check essential files and directories
essential_files=(
    "README.md"
    "DEMO.md"
    "DEVELOPMENT.md"
    "docker-compose.yml"
    ".gitignore"
    ".env.example"
    "Makefile"
    "backend/requirements.txt"
    "backend/app/main.py"
    "frontend/package.json"
    "frontend/next.config.js"
    "frontend/tsconfig.json"
    "infra/cypher_setup.cypher"
)

for file in "${essential_files[@]}"; do
    if [ -f "$file" ]; then
        pass_test "Essential file: $file"
    else
        fail_test "Missing essential file: $file"
    fi
done

# Check directories
essential_dirs=(
    "backend/app"
    "backend/app/routers"
    "backend/app/services"
    "frontend/app"
    "frontend/components"
    "scripts"
    "infra"
)

for dir in "${essential_dirs[@]}"; do
    if [ -d "$dir" ]; then
        pass_test "Essential directory: $dir"
    else
        fail_test "Missing essential directory: $dir"
    fi
done

echo ""
echo "🐍 Backend Validation..."

# Check backend virtual environment
if [ -d "backend/venv" ]; then
    pass_test "Backend virtual environment exists"
    
    # Check if requirements are installed
    if [ -f "backend/venv/pyvenv.cfg" ]; then
        pass_test "Virtual environment is properly configured"
    else
        warn_test "Virtual environment may not be properly configured"
    fi
else
    warn_test "Backend virtual environment not found (run: cd backend && python3 -m venv venv)"
fi

# Check backend configuration
if [ -f "backend/.env" ]; then
    pass_test "Backend environment file exists"
else
    info_test "Backend .env not found (will use root .env)"
fi

# Check Python imports (basic syntax check)
cd backend
python_errors=0
for py_file in $(find app -name "*.py"); do
    if ! python3 -m py_compile "$py_file" 2>/dev/null; then
        fail_test "Python syntax error in $py_file"
        python_errors=$((python_errors + 1))
    fi
done

if [ $python_errors -eq 0 ]; then
    pass_test "All Python files have valid syntax"
fi
cd ..

echo ""
echo "⚛️ Frontend Validation..."

# Check frontend dependencies
if [ -d "frontend/node_modules" ]; then
    pass_test "Frontend dependencies installed"
    
    # Check key packages
    key_packages=("next" "react" "typescript" "tailwindcss")
    for package in "${key_packages[@]}"; do
        if [ -d "frontend/node_modules/$package" ]; then
            pass_test "Package installed: $package"
        else
            fail_test "Missing package: $package"
        fi
    done
else
    fail_test "Frontend dependencies not installed (run: cd frontend && npm install)"
fi

# Check frontend configuration files
frontend_configs=(
    "frontend/.eslintrc.json"
    "frontend/.prettierrc"
    "frontend/postcss.config.js"
    "frontend/tailwind.config.js"
    "frontend/next-env.d.ts"
)

for config in "${frontend_configs[@]}"; do
    if [ -f "$config" ]; then
        pass_test "Frontend config: $(basename $config)"
    else
        fail_test "Missing frontend config: $(basename $config)"
    fi
done

# Check if frontend can compile
if [ -d "frontend/node_modules" ]; then
    cd frontend
    if npm run build --dry-run 2>/dev/null; then
        pass_test "Frontend build configuration valid"
    else
        warn_test "Frontend build may have issues (check with: npm run build)"
    fi
    cd ..
fi

echo ""
echo "🐳 Docker Configuration..."

if [ "$DOCKER_AVAILABLE" = true ]; then
    # Check Docker configuration
    if docker-compose config >/dev/null 2>&1; then
        pass_test "Docker Compose configuration is valid"
    else
        fail_test "Docker Compose configuration has errors"
    fi

    # Check if Docker is running
    if docker info >/dev/null 2>&1; then
        pass_test "Docker daemon is running"
    else
        warn_test "Docker daemon is not running"
    fi
else
    warn_test "Docker not available - manual setup required"
    info_test "Install Docker to use containerized deployment"
fi

echo ""
echo "⚙️ Environment Configuration..."

# Check environment files
if [ -f ".env" ]; then
    pass_test "Root environment file exists"
else
    warn_test "Root .env file not found (copy from .env.example)"
fi

if [ -f "frontend/.env.local" ]; then
    pass_test "Frontend environment file exists"
else
    info_test "Frontend .env.local not found (optional)"
fi

echo ""
echo "📋 Summary"
echo "=========="
echo -e "Tests Passed: ${GREEN}${TESTS_PASSED}${NC}"
echo -e "Tests Failed: ${RED}${TESTS_FAILED}${NC}"

# Calculate success rate
total_tests=$((TESTS_PASSED + TESTS_FAILED))
if [ $total_tests -gt 0 ]; then
    success_rate=$((TESTS_PASSED * 100 / total_tests))
    echo "Success Rate: ${success_rate}%"
fi

echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All validation tests passed! BioNexus is ready to run.${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Start services: docker-compose up -d"
    echo "2. Run demo: ./scripts/run_demo.sh"
    echo "3. Access frontend: http://localhost:3000"
    echo "4. Access backend: http://localhost:8000"
elif [ $TESTS_FAILED -le 3 ]; then
    echo -e "${YELLOW}⚠️ Minor issues detected but project should still work.${NC}"
    echo "Consider fixing the failed tests for optimal experience."
elif [ $TESTS_FAILED -le 10 ]; then
    echo -e "${YELLOW}🔧 Some setup required. Please fix the failed tests.${NC}"
    echo ""
    echo "Common fixes:"
    echo "- Run: ./setup.sh (automated setup)"
    echo "- Install missing dependencies"
    echo "- Create missing configuration files"
else
    echo -e "${RED}🚨 Significant issues detected. Setup required before running.${NC}"
    echo ""
    echo "Recommended actions:"
    echo "1. Run the setup script: ./setup.sh"
    echo "2. Check system requirements in DEVELOPMENT.md"
    echo "3. Ensure all prerequisites are installed"
    exit 1
fi