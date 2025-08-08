## Investor Data MCP Server

A Model Context Protocol (MCP) server that exposes tools, resources, and prompts for fetching and analyzing venture capital investor data from a Supabase-hosted OpenVC dataset.

### Highlights

- **Investor data access**: Names, websites, HQ, countries, stages, cheque sizes, thesis
- **Flexible search**: Filter by investor type, investment stage, country of investment, or HQ location
- **Analytics**: Stage distribution, database stats, thesis theme analysis, similar investors
- **MCP-native**: Tools/resources/prompts consumable by any MCP-compatible client

---

## Requirements

- Python 3.12+
- Supabase project

Environment variables (set in your shell or a `.env` file):

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `SUPABASE_TABLE`
- `PORT` (optional; defaults to `8000`)

Example `.env`:

```env
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-or-service-role-key
SUPABASE_TABLE=dec-2024
PORT=8000
```

---

## Setup

Install dependencies (recommended for the included test clients):

```bash
pip install -r requirements.txt
```

Alternatively, install from `pyproject.toml`:

```bash
pip install .
```

---

## Run the MCP Server Locally

```bash
python server.py
```

On startup, the server prints its MCP endpoint. By default:

- MCP endpoint: `http://localhost:8000/mcp`

Change the port by setting `PORT`.

---

## Available Tools

- `get_investor_data(limit?: int)`
- `search_investors_by_criteria(investor_type?: str, stage?: str, country?: str, hq_location?: str, limit?: int)`
- `get_available_investor_types()`
- `get_available_countries()`
- `get_location_search_guide()`
- `analyze_investment_stages()`
- `find_investors_by_cheque_size(min_amount?: str, max_amount?: str, limit?: int)`
- `analyze_investment_thesis()`
- `get_investor_statistics()`
- `find_similar_investors(investor_name: str, limit?: int)`

Notes:

- `country` accepts common names/codes (e.g., "USA", "UK").
- Cheque size filtering is string-based and approximate.

---

## Resources and Prompts

- Resource: `docs://vc_data_guide`
- Prompt: `analyze_investor_data(investor_data: str)`

---

## Test Locally (LangChain + MCP)

`test_client_local.py` demonstrates connecting a LangChain agent to the local MCP server via `langchain-mcp-adapters` and `ChatGroq`.

Prerequisites:

- Local server running (`python server.py`)
- `.env` contains `GROQ_API_KEY` for ChatGroq

Run:

```bash
python test_client_local.py
```

It exercises multiple tools (investor data, search, analytics) and prints truncated outputs.

---

## Test a Smithery Deployment

`test_client_smithery.py` validates a Smithery-hosted deployment.

Prerequisites in `.env`:

- `SMITHERY_API_KEY`
- `SMITHERY_PROFILE`
- Optional: `GROQ_API_KEY` (for LangChain tests; otherwise skipped)

Run:

```bash
python test_client_smithery.py
```

It first checks a direct MCP connection to a Smithery URL, then (optionally) runs LangChain agent tests. The Smithery build is configured via `smithery.yaml` and the container via `Dockerfile`.

---

## Docker

Build:

```bash
docker build -t investor-data-mcp .
```

Run (provide Supabase env vars):

```bash
docker run --rm -p 8000:8000 \
  -e SUPABASE_URL="https://your-project-id.supabase.co" \
  -e SUPABASE_KEY="your-supabase-key" \
  -e TABLE_NAME="table_1" \
  -e PORT=8000 \
  investor-data-mcp
```

The container exposes the MCP endpoint at `http://localhost:8000/mcp`.

---

## Data Schema Expectations

Expected table (configurable via `SUPABASE_TABLE` env var) with columns such as:

- `Investor name`
- `Website`
- `Global HQ`
- `Countries of investment`
- `Stage of investment`
- `Investment thesis`
- `Investor type`
- `First cheque minimum`
- `First cheque maximum`

Update the `SUPABASE_TABLE` environment variable or selected columns in `server.py` if your schema differs.

---

## Integration Notes

- Transport is `streamable-http`; the MCP endpoint is `/mcp`.
- You can discover tools with an MCP client directly or use LangChain via `langchain-mcp-adapters`.

Minimal MCP client example (see `test_client_local.py` for a full example):

```python
from langchain_mcp_adapters.client import MultiServerMCPClient

client = MultiServerMCPClient({
    "investor_data": {
        "url": "http://localhost:8000/mcp",
        "transport": "streamable_http",
    }
})

tools = await client.get_tools()
```

---

## Troubleshooting

- Ensure `SUPABASE_URL` and `SUPABASE_KEY` are set (env or `.env`).
- Verify the Supabase table (`SUPABASE_TABLE` env var) exists and column names match.
- Set `GROQ_API_KEY` to enable LangChain agent testing.
- Adjust `PORT` if you have port conflicts.

---

## Data Source

The investor data is sourced from [OpenVC](https://openvc.app/), a comprehensive database of venture capital investors worldwide. The dataset was last updated in December 2024, providing current information on investor preferences, investment stages, thesis, and contact details.

## License and Attribution

This server queries an OpenVC-sourced dataset hosted in Supabase. Ensure compliance with data licensing and any applicable terms for your dataset copy.
