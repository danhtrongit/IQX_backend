#!/bin/bash

# Script setup ban đầu cho Backend IQX
# Chạy script này lần đầu tiên để thiết lập project

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")"

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}→ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }
print_error() { echo -e "${RED}✗ $1${NC}"; }

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   IQX Backend Initial Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. Check Python
print_info "Checking Python..."
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    exit 1
fi
PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Python $PYTHON_VERSION found"

# 2. Create virtual environment
if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    fi
else
    print_info "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# 3. Activate and install dependencies
print_info "Installing dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -e ".[dev]"
touch venv/.requirements_installed
print_success "Dependencies installed"

# 4. Setup .env
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        print_info "Creating .env file..."
        cp .env.example .env
        print_success ".env file created"
        print_warning "Please edit .env file with your configuration:"
        echo ""
        cat .env
        echo ""
    else
        print_error ".env.example not found!"
        exit 1
    fi
else
    print_success ".env file already exists"
fi

# 5. Check MySQL
print_info "Please ensure MySQL is running and configured"
source .env
echo ""
echo "Database Configuration:"
echo "  Host: ${MYSQL_HOST:-localhost}"
echo "  Port: ${MYSQL_PORT:-3306}"
echo "  Database: ${MYSQL_DATABASE:-iqx_db}"
echo "  User: ${MYSQL_USER:-iqx}"
echo ""
print_warning "If database doesn't exist, create it with:"
echo "  mysql -u root -p"
echo "  > CREATE DATABASE ${MYSQL_DATABASE:-iqx_db};"
echo "  > CREATE USER '${MYSQL_USER:-iqx}'@'localhost' IDENTIFIED BY 'your_password';"
echo "  > GRANT ALL PRIVILEGES ON ${MYSQL_DATABASE:-iqx_db}.* TO '${MYSQL_USER:-iqx}'@'localhost';"
echo "  > FLUSH PRIVILEGES;"
echo ""
read -p "Press Enter when ready to continue..."

# 6. Run migrations
print_info "Running database migrations..."
alembic upgrade head
print_success "Migrations completed"

# 7. Seed admin user
print_info "Creating admin user..."
python scripts/seed_admin.py
print_success "Admin user created"

# 8. Sync symbols (optional)
echo ""
read -p "Do you want to sync stock symbols from vnstock? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Syncing symbols... (this may take a while)"
    python scripts/sync_symbols.py
    print_success "Symbols synced"
else
    print_warning "Symbols sync skipped"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}   Setup Completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
print_success "Backend is ready to run!"
echo ""
print_info "To start the server:"
echo "  ./start.sh"
echo ""
print_info "Default admin credentials:"
echo "  Email: admin@iqx.local"
echo "  Password: Admin@12345"
echo ""
print_info "API Documentation:"
echo "  http://localhost:8000/docs"
echo ""
