# Simple Demo

Minimal single-agent demo using agntcy-app-sdk with local file-backed directory discovery.

## Files

- `agent.py`: FastMCP server with calculator tools
- `client.py`: discovers CalculatorAgent from directory and calls tools
- `directory.py`: shared directory singleton
- `local_directory.py`: file-backed directory implementation
- `oasf_record.py`: OASF record and AgentCard conversion
- `requirements.txt`: Python dependencies
- `Dockerfile`: deployable container image for server

## Run locally

Install:

```bash
pip install -r requirements.txt
```

Terminal 1:

```bash
python agent.py
```

Terminal 2:

```bash
python client.py
```

## Docker

Build:

```bash
docker build -t agntcy-simple-demo .
```

Run server container:

```bash
docker run --rm -p 8000:8000 agntcy-simple-demo
```
