#!/bin/bash

echo "🚀 Starting Smart Exam Grading System..."

# Function to kill processes on exit
cleanup() {
    echo "Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo "Starting Backend (FastAPI)..."
cd "$(dirname "$0")"
uvicorn backend.main:app --host 0.0.0.0 --port 8000 &

# Wait for backend to be ready (simple sleep)
sleep 2

# Start Frontend
echo "Starting Frontend (React)..."
cd frontend
npm run dev -- --host &

# Wait
wait
