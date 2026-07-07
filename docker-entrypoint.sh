#!/bin/bash
set -e

echo "Starting Lāceni WhatsApp Dashboard..."

# Start FastAPI backend
echo "Starting FastAPI backend..."
cd /app
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &

# Start Next.js frontend
echo "Starting Next.js frontend..."
cd /app/frontend
npm start &

wait
