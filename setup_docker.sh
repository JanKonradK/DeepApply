#!/bin/bash
# Quick Docker setup script for Nyx Venatrix

set -e

echo "🚀 Nyx Venatrix Docker Setup"
echo "=============================="

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your API keys before running!"
    echo ""
    read -p "Press Enter to continue (make sure you've set GROK_API_KEY and OPENAI_API_KEY)..."
fi

# Check for required API keys
if ! grep -q "your-grok-api-key-here" .env 2>/dev/null; then
    echo "✅ API keys appear to be configured"
else
    echo "❌ Please set your API keys in .env file!"
    exit 1
fi

# Pull latest images
echo ""
echo "📦 Pulling Docker images..."
docker compose pull

# Build services
echo ""
echo "🔨 Building services..."
docker compose build

# Start infrastructure only first
echo ""
echo "🗄️  Starting infrastructure (PostgreSQL, Redis, Qdrant)..."
docker compose up -d postgres redis qdrant

# Wait for PostgreSQL to be ready
echo ""
echo "⏳ Waiting for PostgreSQL to be ready..."
until docker compose exec -T postgres pg_isready -U postgres; do
    echo "   Waiting for PostgreSQL..."
    sleep 2
done

echo "✅ PostgreSQL is ready!"

# Run migrations
echo ""
echo "🔄 Running database migrations..."
python run_migrations.py || echo "⚠️  Migrations failed, but continuing..."

# Start all services
echo ""
echo "🚀 Starting all services..."
docker compose up -d

# Show status
echo ""
echo "📊 Service Status:"
docker compose ps

echo ""
echo "✅ Setup complete!"
echo ""
echo "Services available at:"
echo "  - Frontend:  http://localhost:5173"
echo "  - Backend:   http://localhost:3000"
echo "  - Agent API: http://localhost:8000"
echo "  - Qdrant:    http://localhost:6333/dashboard"
echo ""
echo "View logs with: docker compose logs -f"
echo "Stop with:      docker compose down"
echo ""
