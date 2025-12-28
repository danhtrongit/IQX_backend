#!/bin/bash

# Script dừng Backend IQX

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓ $1${NC}"; }
print_info() { echo -e "${BLUE}→ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠ $1${NC}"; }

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Stopping IQX Backend${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Find and kill uvicorn processes
PIDS=$(pgrep -f "uvicorn app.main:app")

if [ -z "$PIDS" ]; then
    print_warning "No backend process found"
    exit 0
fi

print_info "Found backend processes: $PIDS"
echo ""
for PID in $PIDS; do
    print_info "Stopping process $PID..."
    kill $PID 2>/dev/null || kill -9 $PID 2>/dev/null
    print_success "Process $PID stopped"
done

echo ""
print_success "Backend stopped successfully"
