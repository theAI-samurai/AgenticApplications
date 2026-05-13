# AG-UI to A2UI Protocol Translation Layer

This Python module provides a FastAPI route that proxies AG-UI protocol events from the backend, translates them to A2UI protocol messages, and emits them to the frontend.

## Usage
- Import and mount the router in your FastAPI app (or run as a standalone service).
- Set the A2UI frontend to connect to `/a2ui-events` for SSE.

## TODO
- Implement AG-UI → A2UI message translation logic in `translate_agui_to_a2ui()`.
- Optionally, support WebSocket in addition to SSE.
