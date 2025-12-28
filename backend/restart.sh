#!/bin/bash

# Script restart Backend IQX

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

cd "$(dirname "$0")"

print_info() { echo -e "${BLUE}→ $1${NC}"; }

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Restarting IQX Backend${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

print_info "Stopping backend..."
./stop.sh

echo ""
print_info "Starting backend..."
./start.sh
