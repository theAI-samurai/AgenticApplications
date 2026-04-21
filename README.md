# Agntcy Demo

A minimal demo using `agntcy-app-sdk` that shows:

- **OASF record** — standardized agent metadata (skills, domain, version)
- **Agntcy Directory** — agent registration and name-based discovery via `LocalDirectory` (file-backed, drop-in for the real gRPC service)
- **FastMCP server** — exposes tools over HTTP via the MCP protocol
- **MCP client** — discovers the agent through the directory, then calls its tools

## Files

| File | Purpose |
|---|---|
| `oasf_record.py` | OASF agent record + `to_agent_card()` conversion |
| `local_directory.py` | `BaseAgentDirectory` implementation backed by a JSON file |
| `directory.py` | Shared directory singleton (`agent_registry.json`) |
| `agent.py` | FastMCP server — registers in directory, serves on port 8000 |
| `client.py` | MCP client — discovers agent via directory, calls tools |
| `requirements.txt` | Python dependencies |

## Requirements

- Python 3.12+
- pip

## Installation

```bash
pip install -r requirements.txt
```

## How to run

Open **two terminals** in the project directory.

### Terminal 1 — start the agent

```bash
python agent.py
```

Expected output:
```
Starting CalculatorAgent v1.0.0
Domain   : productivity / tool-use
Skills   : ['add', 'multiply', 'celsius_to_fahrenheit']

[Directory] Record pushed → CID: sha256:ea55dd68152b8511
[Directory] Agent discoverable by name: 'CalculatorAgent'

Server listening on http://localhost:8000/mcp  (Ctrl+C to stop)
```

The agent writes its OASF-converted `AgentCard` to `agent_registry.json`.

### Terminal 2 — run the client

```bash
python client.py
```

Expected output:
```
=== Agntcy Demo — Directory-Driven MCP Client ===

[Directory] Searching for agent: 'CalculatorAgent' ...
[Directory] Found: CalculatorAgent v1.0.0
[Directory] Endpoint: http://localhost:8000/mcp
[Directory] Skills  : ['add', 'multiply', 'celsius_to_fahrenheit']

Tools available on agent:
  • add: Add two numbers together.
  • multiply: Multiply two numbers.
  • celsius_to_fahrenheit: Convert a temperature from Celsius to Fahrenheit.

add(42, 8)                     = 50.0
multiply(6, 7)                 = 42.0
celsius_to_fahrenheit(100 °C)  = 212.0 °F
```

The client never uses a hardcoded URL — it searches the directory and reads
the endpoint from the stored `AgentCard`.

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  oasf_record.py                  │
│  OASFRecord  ──to_agent_card()──▶  AgentCard     │
│  (name, version, domain, skills, extensions …)   │
└───────────┬──────────────────────────────────────┘
            │ push on startup          ▲ search / pull
            ▼                          │
┌───────────────────────────────────────────────────┐
│            directory.py / local_directory.py      │
│   LocalDirectory  (agent_registry.json on disk)   │
│   implements BaseAgentDirectory                   │
│   ── drop-in for AgentDirectory (gRPC) ──         │
└───────────────────────────────────────────────────┘
            │                          │
            │ (agent pushes)           │ (client reads endpoint)
            ▼                          │
┌───────────────────┐       ┌──────────┴────────────┐
│     agent.py      │       │       client.py        │
│  FastMCP server   │◀─────▶│  MCP ClientSession     │
│  tools: add,      │ HTTP  │  discover_agent()      │
│   multiply,       │ :8000 │  list_tools()          │
│   celsius_to_f    │       │  call_tool(...)        │
└───────────────────┘       └───────────────────────┘
```

## Key concepts

| Concept | Role in this demo |
|---|---|
| **OASF** | Standardized schema for agent capabilities; enables discovery across distributed systems |
| **OASF → AgentCard** | `to_agent_card()` converts the OASF record into an A2A `AgentCard` for the directory |
| **LocalDirectory** | File-backed `BaseAgentDirectory`; swap one line for the real gRPC `AgentDirectory` |
| **FastMCP** | Simplest way to expose agent tools over the MCP protocol |
| **AgntcyFactory** | Higher-level wrapper for SLIM/NATS/HTTP transports and A2A/MCP protocols |

## Switching to the real Agntcy Directory

Replace one line in `directory.py`:

```python
# Before (local file-backed, no infrastructure needed)
from local_directory import LocalDirectory
directory = LocalDirectory(registry_file="agent_registry.json")

# After (real gRPC service — requires a running agntcy-dir instance)
from agntcy_app_sdk.directory import AgentDirectory
directory = AgentDirectory.from_config(endpoint="127.0.0.1:8888")
```
