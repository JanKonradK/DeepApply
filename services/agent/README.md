# Agent Service: Inference & Instrumentation

This service is the autonomous worker responsible for executing complex browser interactions and performing semantic inference using Large Language Models (LLMs).

## 🔬 Core Technologies

-   **Python 3.13**: Leveraging the latest performance improvements.
-   **Playwright**: Headless browser automation with stealth plugins for fingerprint normalization.
-   **LangChain**: Orchestration of LLM chains and tool usage.
-   **Qdrant**: Vector database for Retrieval-Augmented Generation (RAG).
-   **Prometheus**: Real-time metrics instrumentation.

## 🧠 RAG Engine (`KnowledgeBase`)

The agent utilizes a local-first RAG engine to retrieve context-aware data during execution.

### Prioritization Logic
The engine prioritizes information sources based on their semantic authority:
1.  **CVs** (Weight: 5.0): High-priority biographical data.
2.  **Professional_Info** (Weight: 4.0): Employment history and references.
3.  **Academic_Info** (Weight: 3.0): Educational credentials.
4.  **Personal_Info** (Weight: 2.0): Bio and cover letter context.
5.  **Other_Info** (Weight: 1.0): Auxiliary data.

## 🛡️ Guardrails

To prevent runaway costs and infinite loops, the agent enforces strict token limits:
-   **`MAX_TOKENS_PER_QUESTION`**: Limits the output length of a single reasoning step.
-   **`MAX_TOKENS_PER_APP`**: Limits the total token budget for a single execution run.

## 📊 Metrics

The service exposes a `/metrics` endpoint scraping:
-   `agent_runs_total`: Counter of total executions.
-   `agent_errors_total`: Counter of failed runs.
-   `agent_tokens_total`: Counter of input/output tokens used.
-   `agent_cost_usd_total`: Estimated cost in USD.
-   `agent_duration_seconds`: Histogram of execution latency.
