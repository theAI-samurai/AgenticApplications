# AG-UI Basics

This project demonstrates how to expose simple Python tools through an AG-UI compatible backend and interact with them from a Streamlit UI.

The example reuses the math tools from `mcp_simple`:

- `add(a, b)`
- `subtract(a, b)`

## What AG-UI Does

AG-UI is a protocol for connecting agent backends to user interfaces.

Instead of forcing every frontend to understand a custom agent response format, AG-UI defines standard events that an agent server can stream to the UI. The UI can then react consistently to things like:

- a run starting or finishing
- an assistant message streaming token by token
- a tool call starting
- tool arguments being sent
- a tool result being returned
- backend state changing during the run

In this demo, the AG-UI server streams events such as:

```text
RUN_STARTED
STATE_SNAPSHOT
TOOL_CALL_START
TOOL_CALL_ARGS
TOOL_CALL_RESULT
TEXT_MESSAGE_CONTENT
STATE_DELTA
RUN_FINISHED
```

This makes the UI more transparent. Instead of only seeing the final answer, the frontend can show what the agent is doing while it is doing it.

## AG-UI vs MCP In This Demo

MCP focuses on tool discovery and tool invocation. It lets a client ask, "What tools are available?" and then call one of those tools.

AG-UI focuses on the live agent-to-frontend experience. It lets a backend stream structured events to a UI so the user can see messages, tool calls, state updates, and final results in one consistent format.

In a real application, these can work together:

- MCP can provide tools.
- AG-UI can provide the frontend event stream around the agent run.

## Project Structure

```text
AGUI_basics/
├── agui_server.py
├── mcp_tools_server.py
├── tools.py
├── requirements.txt
├── README.md
└── ui/
    └── streamlit_app.py
```

## File Guide

### `tools.py`

Shared tool implementation.

It contains the actual Python functions:

- `add(a, b)`
- `subtract(a, b)`

It also defines tool metadata used by the AG-UI server.

### `agui_server.py`

The main AG-UI backend.

It runs a FastAPI application with:

- `POST /` - accepts an AG-UI `RunAgentInput`
- `GET /health` - health check
- `GET /tools` - returns available tool metadata

When the UI sends a prompt such as `add 10 and 5`, this server:

1. Parses the user request.
2. Selects the correct tool.
3. Streams AG-UI lifecycle events.
4. Streams tool call events.
5. Runs the Python tool.
6. Streams the assistant response.
7. Sends the final run result.

### `ui/streamlit_app.py`

The Streamlit frontend.

It sends user messages to the AG-UI server and reads the Server-Sent Events response. It displays:

- the chat conversation
- the current synced agent state
- the raw AG-UI events from the last run

The raw event viewer is useful for learning how AG-UI works.

### `mcp_tools_server.py`

A copied FastMCP version of the same math tools.

This file is optional. It is included so you can compare:

- MCP tool calling
- AG-UI event streaming

### `requirements.txt`

Python dependencies for the demo:

- `ag-ui-protocol`
- `fastapi`
- `uvicorn`
- `streamlit`
- `httpx`
- `fastmcp`

## Setup

Use the existing `agntcy` conda environment.

```bash
cd /Users/anankitm/Documents/oracle_repos/AGUI_study/AGUI_basics
conda activate agntcy
pip install -r requirements.txt
```

## Run The AG-UI Server

Start the backend:

```bash
cd /Users/anankitm/Documents/oracle_repos/AGUI_study/AGUI_basics
conda activate agntcy
python agui_server.py
```

By default, the AG-UI server runs at:

```text
http://localhost:8001/
```

Health check:

```text
http://localhost:8001/health
```

Tool metadata:

```text
http://localhost:8001/tools
```

If port `8001` is already in use, run the server on another port:

```bash
cd /Users/anankitm/Documents/oracle_repos/AGUI_study/AGUI_basics
conda activate agntcy
uvicorn agui_server:app --host 127.0.0.1 --port 8011
```

In that case, use this endpoint in the Streamlit sidebar:

```text
http://localhost:8011/
```

## Run The Streamlit UI

Open a second terminal and run:

```bash
cd /Users/anankitm/Documents/oracle_repos/AGUI_study/AGUI_basics
conda activate agntcy
streamlit run ui/streamlit_app.py
```

Streamlit will print a local URL, usually:

```text
http://localhost:8501
```

Open that URL in the browser.

Try prompts like:

```text
add 10 and 5
subtract 10 and 5
what is the difference between 25 and 9
```

## Optional: Run The MCP Server

This is only for comparison with the original MCP-style tool server.

```bash
cd /Users/anankitm/Documents/oracle_repos/AGUI_study/AGUI_basics
conda activate agntcy
python mcp_tools_server.py
```

The MCP endpoint runs at:

```text
http://localhost:8000/mcp
```

## Expected Flow of AGUI

When you enter:

```text
add 10 and 5
```

The backend will:

1. Start an AG-UI run.
2. Emit the current state snapshot.
3. Parse the user request.
4. Emit a tool call for `add`.
5. Execute `add(a=10, b=5)`.
6. Emit the tool result `15`.
7. Stream the assistant message.
8. Finish the run.

The UI will show the final answer:

```text
add(10.0, 5.0) = 15.0
```

The "Last AG-UI events" expander shows the protocol events that produced the answer.
