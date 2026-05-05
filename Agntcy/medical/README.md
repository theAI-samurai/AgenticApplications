# Medical Demo

Medical-domain multi-agent demo with one combined MCP server and two discoverable agent identities.

## Files

- `medical_combined_server.py`: single MCP server exposing both toolsets (port 8100)
- `medical_multiagent_client.py`: discovers agents and orchestrates calls
- `medical_directory.py`: shared directory setup for file mode or daemon mode
- `medical_oasf_records.py`: OASF records for MedicalTriageAgent and MedicationSafetyAgent
- `local_directory.py`: file-backed directory implementation
- `oasf_record.py`: shared OASF record type definitions
- `requirements.txt`: Python dependencies
- `Dockerfile`: deployable server image

## Run locally

Install:

```bash
pip install -r requirements.txt
```

Terminal 1:

```bash
python medical_combined_server.py
```

Terminal 2:

```bash
python medical_multiagent_client.py
```

## Docker

Build:

```bash
docker build -t agntcy-medical-demo .
```

Run server container:

```bash
docker run --rm -p 8100:8100 agntcy-medical-demo
```
