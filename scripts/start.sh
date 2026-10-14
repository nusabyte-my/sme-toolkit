#!/bin/bash

echo "========================================"
echo "SME Toolkit - Starting Servers"
echo "========================================"
echo

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Function to cleanup on exit
cleanup() {
    echo
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo "Starting Backend Server (port 8000)..."
cd "$PROJECT_DIR/sme-toolkit-backend"
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start Frontend
echo "Starting Frontend Server (port 5173)..."
cd "$PROJECT_DIR"
npm run dev &
FRONTEND_PID=$!

echo
echo "========================================"
echo "Servers Started!"
echo "========================================"
echo
echo "Backend: http://localhost:8000"
echo "  - API Docs: http://localhost:8000/docs"
echo
echo "Frontend: http://localhost:5173"
echo
echo "Press Ctrl+C to stop both servers"
echo

# Wait for both processes
wait
