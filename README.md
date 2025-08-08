# VC Data MCP Server

A Model Context Protocol (MCP) server that provides tools and resources for fetching and analyzing venture capital investor data from the OpenVC database.

## Features

- **Investor Data Access**: Fetch comprehensive investor information including names, websites, investment stages, and thesis
- **Advanced Search**: Search investors by type, investment stage, or country
- **Data Analysis**: Get insights about the VC investment landscape
- **Real-time Updates**: Access to the latest investor data from OpenVC database

## Setup

1. Install dependencies:

```bash
pip install -e .
```

2. Create a `.env` file in the project root with your Supabase credentials:

```
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-supabase-anon-key-or-service-role-key
PORT=8003
```

You can find the Supabase values in your Supabase project dashboard under Settings > API.

## Running the MCP Server

Start the server:

```bash
python main.py
```

The server will run on `http://localhost:8003` with the MCP endpoint available at `http://localhost:8003/mcp`.

## Available Tools

### 1. `get_investor_data`

Fetches investor data from the OpenVC database.

**Parameters:**

- `limit` (Optional[int]): Maximum number of records to return

**Returns:** Formatted string containing investor records with:

- Investor name
- Website
- Global HQ
- Countries of investment
- Stage of investment
- Investment thesis
- Investor type
- First cheque minimum and maximum

### 2. `search_investors_by_criteria`

Search for investors based on specific criteria.

**Parameters:**

- `investor_type` (Optional[str]): Type of investor (e.g., "Angel", "VC", "PE")
- `stage` (Optional[str]): Investment stage (e.g., "Seed", "Series A", "Growth")
- `country` (Optional[str]): Country of investment
- `limit` (Optional[int]): Maximum number of records to return

**Returns:** Formatted string containing matching investor records

## Available Resources

### `docs://vc_data_guide`

Provides guidance on interpreting VC investor data, including:

- Investor types (Angel, VC, PE, CVC)
- Investment stages (Pre-seed, Seed, Series A, etc.)
- Understanding first cheque ranges
- Interpreting investment thesis

## Available Prompts

### `analyze_investor_data`

Analyzes VC investor data and provides insights about the investment landscape, including:

- Geographic distribution of investors
- Investment stage preferences
- Typical investment sizes
- Investment thesis patterns
- Notable trends and insights

## Example Usage

The MCP server can be integrated with any MCP-compatible client. The tools are designed to be used when users ask for:

- Investor information
- VC data
- Startup funding data
- Investment landscape analysis
- Finding investors by specific criteria

## Data Source

This server connects to the OpenVC database, which contains comprehensive information about venture capital investors worldwide, including their investment preferences, thesis, and contact information.
