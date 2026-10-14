#!/bin/bash

echo "========================================"
echo "SME Toolkit - Quick Setup Script"
echo "========================================"
echo

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python 3 is not installed"
    echo "Please install Python 3.10+ from https://www.python.org/downloads/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "[ERROR] Node.js is not installed"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "[OK] Python and Node.js found"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Setup Backend
echo "========================================"
echo "Setting up Backend..."
echo "========================================"
cd "$PROJECT_DIR/sme-toolkit-backend"

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing Python dependencies..."
pip install -r requirements.txt

if [ ! -f ".env" ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    echo
    echo "[IMPORTANT] Please edit sme-toolkit-backend/.env and add your API keys!"
    echo "At minimum, add your GEMINI_API_KEY"
    echo
fi

echo
echo "========================================"
echo "Setting up Frontend..."
echo "========================================"
cd "$PROJECT_DIR"

echo "Installing npm dependencies..."
npm install

if [ ! -f ".env.local" ]; then
    echo "Creating .env.local..."
    echo "VITE_API_BASE_URL=http://localhost:8000" > .env.local
fi

echo
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo
echo "Next steps:"
echo "1. Edit sme-toolkit-backend/.env and add your GEMINI_API_KEY"
echo "2. Run ./scripts/start.sh to start both servers"
echo
