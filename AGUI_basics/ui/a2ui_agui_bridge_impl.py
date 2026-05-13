from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
import httpx
import asyncio
import json

router = APIRouter()

AGUI_EVENTS_URL = "http://localhost:8000/events"  # AG-UI backend SSE endpoint

async def translate_agui_to_a2ui(agui_event: dict) -> dict:
    # TODO: Implement actual translation logic
    # For now, just pass through (not A2UI compliant)
    return agui_event

async def agui_to_a2ui_event_stream():
    async with httpx.AsyncClient(timeout=None) as client:
        async with client.stream("GET", AGUI_EVENTS_URL) as response:
            async for line in response.aiter_lines():
                if line.startswith("data:"):
                    try:
                        agui_event = json.loads(line[5:].strip())
                        a2ui_event = await translate_agui_to_a2ui(agui_event)
                        yield f"data: {json.dumps(a2ui_event)}\n\n"
                    except Exception as e:
                        continue

@router.get("/a2ui-events")
async def a2ui_events(request: Request):
    return StreamingResponse(agui_to_a2ui_event_stream(), media_type="text/event-stream")
