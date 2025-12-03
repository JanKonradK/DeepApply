# 🚀 Nyx Venatrix Quick Start Guide

## Prerequisites

- Docker & Docker Compose
- Python 3.12+
- Chrome browser (for testing)
- API Keys: OPENAI_API_KEY, GROK_API_KEY (optional: TWOCAPTCHA_API_KEY, TELEGRAM_BOT_TOKEN)

## 1. Start Shared Infrastructure

The database infrastructure can be shared across projects:

```bash
cd infrastructure
docker-compose -f docker-compose.infrastructure.yml up -d
```

This starts:
- PostgreSQL 16 with pgvector (port 5432)
- Redis 7 (port 6379)
- Qdrant vector database (ports 6333, 6334)

Check status:
```bash
docker-compose -f docker-compose.infrastructure.yml ps
```

View logs:
```bash
docker-compose -f docker-compose.infrastructure.yml logs -f
```

## 2. Configure Environment

Create `.env` file in project root:

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key
GROK_API_KEY=your-grok-key
AGENT_MODEL=grok-beta

# Optional - for CAPTCHA solving
TWOCAPTCHA_API_KEY=your-2captcha-key

# Optional - for notifications
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id

# Optional - for IDE Chrome testing
CHROME_CDP_URL=http://localhost:9222

# Database (auto-configured if using infrastructure)
DATABASE_URL=postgres://postgres:postgres@localhost:5432/nyx_venatrix
```

## 3. Install Python Dependencies

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install agent dependencies
pip install -r services/agent/requirements.txt

# Install persistence dependencies
pip install -r services/persistence/requirements.txt
```

## 4. Run Tests

```bash
# Run all unit tests
python3 -m unittest discover tests/

# Run service tests specifically
python3 -m unittest tests/test_services.py

# Run persistence tests
python3 -m unittest tests/test_persistence.py

# Run agent tests
python3 -m unittest tests/test_agents.py
```

## 5. Test Chrome CDP Connection (Optional)

If using IDE Chrome for browser automation:

```bash
# Run the CDP test script
python3 tests/test_chrome_cdp.py
```

This will test connecting to Chrome running with remote debugging.

## 6. Start the Agent Service

```bash
cd services/agent

# Start the FastAPI server
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API:
- **API**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Docs**: http://localhost:8000/docs
- **Metrics**: http://localhost:8000/metrics

## 7. API Usage Examples

### Create a Session

```bash
curl -X POST http://localhost:8000/sessions \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "123e4567-e89b-12d3-a456-426614174000",
    "session_name": "Test Session",
    "max_applications": 50,
    "max_parallel_agents": 5
  }'
```

### Stop a Session

```bash
curl -X POST http://localhost:8000/sessions/{session_id}/stop
```

### Check Health

```bash
curl http://localhost:8000/health
```

## 8. Run End-to-End Test

```bash
# Run the E2E workflow test
python3 tests/e2e_workflow.py

# With real database
python3 tests/e2e_workflow.py --real-db

# With visible browser
python3 tests/e2e_workflow.py --visible
```

## 9. Database Management

### Access PostgreSQL

```bash
# Connect to database
docker exec -it shared_postgres psql -U postgres -d nyx_venatrix

# Run a query
docker exec -it shared_postgres psql -U postgres -d nyx_venatrix -c "SELECT COUNT(*) FROM applications;"
```

### View Qdrant Dashboard

Open browser: http://localhost:6333/dashboard

### Access Redis

```bash
docker exec -it shared_redis redis-cli
```

## 10. Monitoring

### Prometheus Metrics

Metrics are exposed at: http://localhost:8000/metrics

Example metrics:
- `agent_runs_total` - Total application runs
- `agent_errors_total` - Total errors
- `agent_duration_seconds` - Execution duration
- `match_scores` - Match score distribution

### Logs

```bash
# Infrastructure logs
cd infrastructure
docker-compose -f docker-compose.infrastructure.yml logs -f

# Application logs
# Logs are output to console with Rich formatting
```

## 11. Cleanup

### Stop Services

```bash
# Stop infrastructure
cd infrastructure
docker-compose -f docker-compose.infrastructure.yml down

# Remove volumes (WARNING: deletes data)
docker-compose -f docker-compose.infrastructure.yml down -v
```

### Stop Agent Service

```bash
# Press Ctrl+C in the terminal running uvicorn
```

## Troubleshooting

### Database Connection Issues

1. Ensure infrastructure is running:
   ```bash
   docker ps | grep shared_postgres
   ```

2. Check database logs:
   ```bash
   docker logs shared_postgres
   ```

### CAPTCHA Solver Not Working

1. Verify API key is set in `.env`
2. Check 2captcha balance:
   ```python
   from services.agent.src.captcha import CaptchaSolver
   solver = CaptchaSolver()
   print(solver.get_balance())
   ```

### Browser Automation Issues

1. For WSL, use IDE Chrome via CDP
2. Set `CHROME_CDP_URL` in `.env`
3. Run test: `python3 tests/test_chrome_cdp.py`

### Import Errors

Ensure you're in the virtual environment:
```bash
source .venv/bin/activate
which python  # Should show .venv/bin/python
```

## Next Steps

- Review `TODO.md` for remaining features
- Check `BUGS.md` for known issues
- Read `infrastructure/README.md` for database details
- Explore API documentation at `/docs` endpoint

## Support

For issues or questions:
1. Check documentation in project directory
2. Review test files in `tests/` for examples
3. Check commit history for recent changes
