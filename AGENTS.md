# AGENTS.md

Guidance for AI coding agents (Cursor, Claude Code, etc.) working in this repo.

## Project

Python learning / experimentation workspace for **LangChain agents**, **LangGraph**, and **MCP servers**.

- Python `>=3.12`
- Package manager: **`uv`** (source of truth is `pyproject.toml` + `uv.lock`)
- `requirements.txt` is a loose checklist only — prefer `uv add <package>` over editing it by hand

## Layout

```
mcpAndAgents/
├── AI Projects/          # Standalone agent demos (e.g. AirBnbListings)
├── scripts/              # Shared tools + MCP servers (yahoo finance, base_tools)
├── langchain/            # LangChain experiments
├── TestConnections/      # Connectivity smoke tests
├── data/                 # Local data assets
├── pyproject.toml        # Dependencies (use this)
├── .env                  # Secrets (never commit)
└── AGENTS.md
```

## Commands

```bash
# Install / sync deps
uv sync

# Add a dependency
uv add <package>

# Run a script
uv run path/to/script.py
uv run "AI Projects/AirBnbListings/airbnb_mcp.py"
```

Always use `uv run` so the project venv is used.

## Environment & secrets

- Load secrets with `python-dotenv` (`load_dotenv()`).
- Never commit: `.env`, `**/gcp-oauth.keys.json`, `*oauth*.json`, `*credentials*.json`, service-account keys.
- Common env vars:
  - `GEMINI_API_KEY` — Google / LangChain Gemini
  - `WEATHER_API_KEY` — WeatherAPI.com (optional)
  - `OLLAMA_API_KEY` — required for `ollama.web_search` (cloud API, not local Ollama)
  - LangSmith: `LANGSMITH_API_KEY`, `LANGSMITH_TRACING`, etc.

## LangChain / agent conventions

- Prefer `langchain.agents.create_agent` + `system_prompt=` (not legacy `prompt=`).
- `create_agent` is **sync** — do not `await` it. Await `agent.ainvoke(...)`.
- Models: `ChatGoogleGenerativeAI` from `langchain_google_genai`.
- Gemini often returns **content blocks** (`list[{"type":"text","text":...}]`). Print with `message.text` or an `extract_text()` helper — not raw `.content`.
- Shared tools live in `scripts/base_tools.py`. Scripts under nested folders may need the repo root on `sys.path` if they import `scripts.*`.

## MCP (`langchain-mcp-adapters`)

`MultiServerMCPClient` expects a flat server map with explicit `transport`:

```python
MultiServerMCPClient({
    "airbnb": {
        "transport": "stdio",
        "command": "npx",
        "args": ["-y", "@openbnb/mcp-server-airbnb", "--ignore-robots-txt"],
    }
})
```

Do **not** wrap servers under `"mcpServers"` (that is Cursor/Claude Desktop config shape, not this client).

Reference implementation: `scripts/yahoo_mcp.py`.

## Coding preferences

- Prefer small, focused scripts over large frameworks.
- Keep demos runnable with `uv run`.
- Match existing style in nearby files.
- Do not commit secrets, oauth key files, or `.env`.
- Do not invent API keys; tell the user which env var is missing.
- Avoid drive-by refactors unrelated to the task.

## When stuck on tools

| Symptom | Likely cause |
|---------|----------------|
| `No module named 'langchain_google_genai'` | Package not in `pyproject.toml` / not installed via `uv add` |
| MCP `Missing 'transport'` | Wrong client config shape — add `"transport": "stdio"` |
| Ollama web search auth error | Missing `OLLAMA_API_KEY` |
| WeatherAPI 401 | Invalid `WEATHER_API_KEY` |
| Printed `[{'type':'text',...}]` | Use `.text` / extract text blocks from Gemini messages |
