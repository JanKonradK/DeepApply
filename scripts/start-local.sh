#!/bin/bash
set -e

# Check if concurrently is installed
if ! command -v concurrently &> /dev/null; then
    echo "Installing concurrently..."
    npm install -g concurrently
fi

echo "🚀 Starting Local Services..."

# Ensure infrastructure is running
if ! docker ps | grep -q "shared_postgres"; then
    echo "⚠️  Infrastructure not running. Starting..."
    docker compose -f docker-compose.db.yml up -d
fi

# Start services
concurrently \
    --names "BACKEND,AGENT,FRONTEND" \
    --prefix-colors "blue,green,magenta" \
    "cd services/backend && npm run dev" \
    "source .venv/bin/activate && cd services/agent && uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload" \
    "cd services/frontend && npm run dev"
