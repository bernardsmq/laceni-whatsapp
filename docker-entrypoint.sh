#!/bin/bash
set -e

echo "Starting Lāceni WhatsApp Dashboard..."

# Start FastAPI backend
echo "Starting FastAPI backend on port 8000..."
cd /app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start Next.js frontend
echo "Starting Next.js frontend on port 3000..."
cd /app/frontend
npm start &
FRONTEND_PID=$!

# Give services time to start
sleep 3

# Start nginx reverse proxy
echo "Starting nginx reverse proxy on port 8080..."
nginx -g 'daemon off;' &
NGINX_PID=$!

echo "Services started:"
echo "  Backend (FastAPI): PID $BACKEND_PID on port 8000"
echo "  Frontend (Next.js): PID $FRONTEND_PID on port 3000"
echo "  Reverse Proxy (nginx): PID $NGINX_PID on port 8080"

wait $NGINX_PID
