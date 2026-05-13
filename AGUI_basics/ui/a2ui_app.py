"""Standalone A2UI browser app for the AG-UI basics demo."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
import json
import uuid

import httpx
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse

APP_DIR = Path(__file__).resolve().parent
HTML_FILE = APP_DIR / "a2ui_client.html"
DEFAULT_AGUI_ENDPOINT = "http://localhost:8001/"

app = FastAPI(title="AG-UI Basics A2UI App")


def _build_a2ui_surface(status: str, output: str) -> dict:
    return {
        "surfaceUpdate": {
            "surfaceId": "main",
            "components": [
                {
                    "id": "root",
                    "component": {"Column": {"children": {"explicitList": ["title", "status", "output"]}}},
                },
                {
                    "id": "title",
                    "component": {
                        "Text": {
                            "text": {
                                "literalString": "A2UI Renderer (translated from AG-UI events)"
                            }
                        }
                    },
                },
                {
                    "id": "status",
                    "component": {"Text": {"text": {"literalString": f"Status: {status}"}}},
                },
                {
                    "id": "output",
                    "component": {"Text": {"text": {"literalString": output}}},
                },
            ],
        }
    }


def _extract_agui_data_lines(buffer: str) -> tuple[list[dict], str]:
    events: list[dict] = []
    while "\n\n" in buffer:
        raw_event, buffer = buffer.split("\n\n", 1)
        data_lines = [line[5:].strip() for line in raw_event.splitlines() if line.startswith("data:")]
        if not data_lines:
            continue
        payload = "\n".join(data_lines).strip()
        if not payload:
            continue
        try:
            events.append(json.loads(payload))
        except json.JSONDecodeError:
            continue
    return events, buffer


def _pick(event: dict, *names: str, default: str = "") -> str:
    for name in names:
        value = event.get(name)
        if value not in (None, ""):
            return str(value)
    return default


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/")
async def index() -> HTMLResponse:
    return HTMLResponse(HTML_FILE.read_text(encoding="utf-8"))


@app.get("/a2ui")
async def a2ui() -> HTMLResponse:
    return HTMLResponse(HTML_FILE.read_text(encoding="utf-8"))


@app.post("/api/tools")
async def api_tools(request: Request) -> JSONResponse:
    body = await request.json()
    endpoint = str(body.get("endpoint") or DEFAULT_AGUI_ENDPOINT).rstrip("/")
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(f"{endpoint}/tools")
        response.raise_for_status()
        payload = response.json()
    return JSONResponse({"tools": payload.get("tools", [])})


@app.post("/api/run")
async def api_run(request: Request) -> StreamingResponse:
    body = await request.json()
    endpoint = str(body.get("endpoint") or DEFAULT_AGUI_ENDPOINT).rstrip("/")
    payload = body.get("payload") or {}

    async def event_stream() -> AsyncIterator[bytes]:
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{endpoint}/",
                json=payload,
                headers={"Accept": "text/event-stream"},
            ) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    if chunk:
                        yield chunk

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/a2ui-events")
async def a2ui_events(request: Request, prompt: str = "add 10 and 5") -> StreamingResponse:
    endpoint = str(request.query_params.get("endpoint") or DEFAULT_AGUI_ENDPOINT).rstrip("/")

    print(
        f"[a2ui_app.a2ui_events] prompt={prompt!r}, agui_endpoint={endpoint!r}",
        flush=True,
    )

    payload = {
        "threadId": f"thread_{uuid.uuid4().hex}",
        "runId": f"run_{uuid.uuid4().hex}",
        "state": {},
        "messages": [
            {
                "id": f"msg_{uuid.uuid4().hex}",
                "role": "user",
                "content": prompt,
            }
        ],
        "tools": [],
        "context": [],
        "forwardedProps": {},
    }

    async def event_stream() -> AsyncIterator[str]:
        status = "running"
        output_text = ""

        print("[a2ui_app.a2ui_events] emitting beginRendering", flush=True)
        yield f"data: {json.dumps({'beginRendering': {'surfaceId': 'main', 'root': 'root'}})}\n\n"
        print("[a2ui_app.a2ui_events] emitting initial surfaceUpdate", flush=True)
        yield f"data: {json.dumps(_build_a2ui_surface(status=status, output='Running AG-UI agent...'))}\n\n"

        buffer = ""
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{endpoint}/",
                json=payload,
                headers={"Accept": "text/event-stream"},
            ) as response:
                response.raise_for_status()
                print(f"[a2ui_app.a2ui_events] connected to AG-UI: status={response.status_code}", flush=True)
                async for chunk in response.aiter_text():
                    if not chunk:
                        continue
                    print(f"[a2ui_app.a2ui_events] received AG-UI chunk: {chunk[:400]!r}", flush=True)
                    buffer += chunk
                    parsed_events, buffer = _extract_agui_data_lines(buffer)
                    for event in parsed_events:
                        print(f"[a2ui_app.a2ui_events] parsed AG-UI event: {event!r}", flush=True)
                        event_type = _pick(event, "type", default="").upper()
                        if not event_type:
                            for key in ("toolCallStart", "toolCallArgs", "toolCallEnd", "toolCallResult", "textMessageContent", "runError", "runFinished"):
                                if key in event:
                                    event_type = key.upper()
                                    event = event.get(key) if isinstance(event.get(key), dict) else event
                                    break

                        if event_type in {"TEXT_MESSAGE_CONTENT", "TEXTMESSAGECONTENT"}:
                            output_text += _pick(event, "delta", default="")
                        elif event_type in {"TOOL_CALL_START", "TOOLCALLSTART"}:
                            tool_name = _pick(event, "toolCallName", "tool_call_name", "tool_name", default="tool")
                            status = f"running {tool_name}"
                            print(f"[a2ui_app.a2ui_events] tool call started: {tool_name}", flush=True)
                        elif event_type in {"TOOL_CALL_RESULT", "TOOLCALLRESULT"}:
                            output_text = _pick(event, "content", default=output_text)
                            print(f"[a2ui_app.a2ui_events] tool call result: {output_text}", flush=True)
                        elif event_type in {"RUN_FINISHED", "RUNFINISHED"}:
                            status = "finished"
                            result_raw = event.get("result") if isinstance(event, dict) else None
                            if isinstance(result_raw, dict) and result_raw.get("answer"):
                                output_text = str(result_raw.get("answer"))
                            print(f"[a2ui_app.a2ui_events] run finished: {result_raw!r}", flush=True)
                        elif event_type in {"RUN_ERROR", "RUNERROR"}:
                            status = "error"
                            output_text = _pick(event, "message", default="Unknown error")
                            print(f"[a2ui_app.a2ui_events] run error: {output_text}", flush=True)
                        else:
                            print(f"[a2ui_app.a2ui_events] ignored event type={event_type!r}", flush=True)

                        yield f"data: {json.dumps(_build_a2ui_surface(status=status, output=output_text or '...'))}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8502)
