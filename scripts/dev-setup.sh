#!/bin/bash
set -e

echo "🚀 Starting Development Setup..."

# 1. Python Setup
echo "🐍 Setting up Python environment..."
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r services/agent/requirements.txt
playwright install chromium

# 2. Backend Setup
echo "📦 Setting up Backend..."
cd services/backend
if [ ! -f ".env" ]; then
    cp .env.example .env
fi
npm install
cd ../..

# 3. Frontend Setup
echo "🎨 Setting up Frontend..."
cd services/frontend
npm install
cd ../..

echo "✅ Setup Complete!"
echo "Run ./scripts/start-local.sh to start services."
