#!/bin/bash

# Script tự động chạy dự án Backend IQX
# Author: IQX Team
# Description: Tự động setup và chạy backend FastAPI

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Change to backend directory
cd "$(dirname "$0")"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   IQX Backend Auto Start Script${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Function to print colored messages
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_info() {
    echo -e "${BLUE}→ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

# Check Python version
print_info "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    print_warning "Virtual environment not found. Creating..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_success "Virtual environment found"
fi

# Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Check if requirements are installed
print_info "Checking dependencies..."
if [ ! -f "venv/.requirements_installed" ]; then
    print_warning "Dependencies not installed. Installing..."
    pip install --upgrade pip
    pip install -e ".[dev]"
    touch venv/.requirements_installed
    print_success "Dependencies installed"
else
    print_success "Dependencies already installed"
fi

# Check .env file
if [ ! -f ".env" ]; then
    print_warning ".env file not found"
    if [ -f ".env.example" ]; then
        print_info "Copying .env.example to .env..."
        cp .env.example .env
        print_warning "Please configure .env file with your MySQL credentials"
        print_warning "Run: nano .env or vim .env"
        exit 1
    else
        print_error ".env.example not found!"
        exit 1
    fi
else
    print_success ".env file found"
fi

# Check MySQL connection
print_info "Checking MySQL connection..."
source .env
if command -v mysql &> /dev/null; then
    if mysql -h"${MYSQL_HOST:-localhost}" -P"${MYSQL_PORT:-3306}" -u"${MYSQL_USER:-iqx}" -p"${MYSQL_PASSWORD}" -e "USE ${MYSQL_DATABASE:-iqx_db};" 2>/dev/null; then
        print_success "MySQL connection OK"
    else
        print_warning "Cannot connect to MySQL database"
        print_info "Please make sure:"
        print_info "  1. MySQL is running"
        print_info "  2. Database '${MYSQL_DATABASE:-iqx_db}' exists"
        print_info "  3. User has proper permissions"
        echo ""
        read -p "Continue anyway? (y/n) " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
else
    print_warning "MySQL client not found, skipping database check"
fi

# Run migrations
print_info "Running database migrations..."
if alembic upgrade head; then
    print_success "Migrations completed"
else
    print_warning "Migration failed (may be normal if already up to date)"
fi

# Check if admin user exists
print_info "Checking admin user..."
if [ -f "scripts/seed_admin.py" ]; then
    python scripts/seed_admin.py 2>/dev/null || print_warning "Admin seeding skipped (may already exist)"
fi

# Parse command line arguments
HOST="${1:-0.0.0.0}"
PORT="${2:-8000}"
RELOAD_FLAG="--reload"

if [ "$3" = "--no-reload" ]; then
    RELOAD_FLAG=""
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Starting Backend Server...${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
print_info "Host: ${HOST}"
print_info "Port: ${PORT}"
print_info "API Docs: http://localhost:${PORT}/docs"
print_info "Test Page: http://localhost:${PORT}/test-realtime"
echo ""
print_warning "Press Ctrl+C to stop the server"
echo ""

# Start the server
uvicorn app.main:app $RELOAD_FLAG --host "$HOST" --port "$PORT"
