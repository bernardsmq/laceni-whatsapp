#!/bin/bash
set -e

echo "Starting Lāceni WhatsApp Dashboard..."

# Start FastAPI backend on port 8000
echo "Starting FastAPI backend on port 8000..."
cd /app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Next.js frontend on port 3000
echo "Starting Next.js frontend on port 3000..."
cd /app/frontend
npm start &
FRONTEND_PID=$!

echo "Services started. Access at http://localhost:3000"
wait
