# Agent Service

The core intelligence of Nyx Venatrix. This service handles the entire lifecycle of a job application, from ingestion to submission.

## Components

### `src/matching/`
**Profile Matcher**: Uses OpenAI embeddings (`text-embedding-3-small`) to compute cosine similarity between your profile and job descriptions. Caches profile embeddings for performance.

### `src/planning/`
**Effort Planner**: Determines the appropriate effort level (Low, Medium, High) based on match scores and company tiers defined in `effort_policy.yml`.

### `src/generation/`
**Answer Generator**: Uses LLMs (Grok/GPT-4) to generate context-aware cover letters and answers to screening questions. Quality varies by effort level.

### `src/agents/`
**Enhanced Form Filler**: A browser automation agent (using `browser-use`) that navigates job sites and fills forms. Includes stealth features like randomized delays and human-like typing.

### `src/qa/`
**QA Agent**: Validates all generated content against your `profile.json`. Checks for hallucinations (claiming skills you don't have) and consistency violations.

### `src/concurrency/`
**Ray Worker Pool**: Manages parallel execution of applications using Ray actors. Supports up to 5 concurrent workers with isolated error handling.

### `src/observability/`
**Trackers**: Integrations for MLflow (metrics/experiments) and Langfuse (LLM traces).

### `src/session/`
**Session Manager**: Handles batch execution of applications, tracking progress and generating digest summaries.

## Running

```bash
# Install dependencies
pip install -r requirements.txt

# Start API
uvicorn src.main:app --reload
```
