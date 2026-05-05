"""Minimal AG-UI server that streams tool execution events over SSE."""

from __future__ import annotations

import asyncio
import json
import re
import uuid
import warnings
from collections.abc import AsyncIterator
from typing import Any

import uvicorn
from ag_ui.core import (
    EventType,
    RunAgentInput,
    RunErrorEvent,
    RunFinishedEvent,
    RunStartedEvent,
    StateDeltaEvent,
    StateSnapshotEvent,
    StepFinishedEvent,
    StepStartedEvent,
    TextMessageContentEvent,
    TextMessageEndEvent,
    TextMessageStartEvent,
    ToolCallArgsEvent,
    ToolCallEndEvent,
    ToolCallResultEvent,
    ToolCallStartEvent,
)
from ag_ui.encoder import EventEncoder
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic.warnings import UnsupportedFieldAttributeWarning

from tools import TOOL_DEFINITIONS, TOOLS


warnings.filterwarnings("ignore", category=UnsupportedFieldAttributeWarning)

app = FastAPI(title="AG-UI Basics Math Agent")


@app.get("/health")
async def health() -> JSONResponse:
    return JSONResponse({"status": "ok"})


@app.get("/tools")
async def list_tools() -> JSONResponse:
    return JSONResponse({"tools": TOOL_DEFINITIONS})


def _message_text(message: Any) -> str:
    content = getattr(message, "content", None)
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            text = getattr(item, "text", None)
            if text is None and isinstance(item, dict):
                text = item.get("text")
            if text:
                parts.append(str(text))
        return " ".join(parts)
    return str(content or "")


def _latest_user_text(input_data: RunAgentInput) -> str:
    for message in reversed(input_data.messages):
        role = getattr(message, "role", None)
        if role == "user":
            return _message_text(message)
    return ""


def _parse_tool_request(text: str) -> tuple[str, dict[str, float]]:
    numbers = [float(value) for value in re.findall(r"[-+]?\d*\.?\d+", text)]
    if len(numbers) < 2:
        raise ValueError("Please provide two numbers, for example: add 10 and 5.")

    lower_text = text.lower()
    if any(word in lower_text for word in ("subtract", "minus", "difference")):
        tool_name = "subtract"
    else:
        tool_name = "add"

    return tool_name, {"a": numbers[0], "b": numbers[1]}


def _chunk_text(text: str, size: int = 24) -> list[str]:
    return [text[index : index + size] for index in range(0, len(text), size)] or [text]


async def _stream_text(
    encoder: EventEncoder,
    message_id: str,
    text: str,
) -> AsyncIterator[str]:
    yield encoder.encode(
        TextMessageStartEvent(
            type=EventType.TEXT_MESSAGE_START,
            message_id=message_id,
            role="assistant",
        )
    )
    for chunk in _chunk_text(text):
        if chunk:
            yield encoder.encode(
                TextMessageContentEvent(
                    type=EventType.TEXT_MESSAGE_CONTENT,
                    message_id=message_id,
                    delta=chunk,
                )
            )
            await asyncio.sleep(0.03)
    yield encoder.encode(
        TextMessageEndEvent(
            type=EventType.TEXT_MESSAGE_END,
            message_id=message_id,
        )
    )


@app.post("/")
async def run_agent(input_data: RunAgentInput, request: Request) -> StreamingResponse:
    encoder = EventEncoder(accept=request.headers.get("accept"))

    async def event_generator() -> AsyncIterator[str]:
        try:
            yield encoder.encode(
                RunStartedEvent(
                    type=EventType.RUN_STARTED,
                    thread_id=input_data.thread_id,
                    run_id=input_data.run_id,
                    parent_run_id=input_data.parent_run_id,
                )
            )

            current_state = dict(input_data.state or {})
            current_state.setdefault("available_tools", [tool["name"] for tool in TOOL_DEFINITIONS])
            yield encoder.encode(
                StateSnapshotEvent(
                    type=EventType.STATE_SNAPSHOT,
                    snapshot=current_state,
                )
            )

            yield encoder.encode(
                StepStartedEvent(
                    type=EventType.STEP_STARTED,
                    step_name="parse-user-request",
                )
            )
            user_text = _latest_user_text(input_data)
            tool_name, arguments = _parse_tool_request(user_text)
            yield encoder.encode(
                StepFinishedEvent(
                    type=EventType.STEP_FINISHED,
                    step_name="parse-user-request",
                )
            )

            message_id = f"msg_{uuid.uuid4().hex}"
            tool_call_id = f"tool_{uuid.uuid4().hex}"
            yield encoder.encode(
                ToolCallStartEvent(
                    type=EventType.TOOL_CALL_START,
                    tool_call_id=tool_call_id,
                    tool_call_name=tool_name,
                    parent_message_id=message_id,
                )
            )
            yield encoder.encode(
                ToolCallArgsEvent(
                    type=EventType.TOOL_CALL_ARGS,
                    tool_call_id=tool_call_id,
                    delta=json.dumps(arguments),
                )
            )
            yield encoder.encode(
                ToolCallEndEvent(
                    type=EventType.TOOL_CALL_END,
                    tool_call_id=tool_call_id,
                )
            )

            result = await TOOLS[tool_name](**arguments)
            yield encoder.encode(
                ToolCallResultEvent(
                    type=EventType.TOOL_CALL_RESULT,
                    message_id=message_id,
                    tool_call_id=tool_call_id,
                    content=str(result),
                    role="tool",
                )
            )

            yield encoder.encode(
                StateDeltaEvent(
                    type=EventType.STATE_DELTA,
                    delta=[
                        {"op": "replace" if "last_result" in current_state else "add", "path": "/last_result", "value": result},
                        {"op": "replace" if "last_tool" in current_state else "add", "path": "/last_tool", "value": tool_name},
                    ],
                )
            )

            answer = f"{tool_name}({arguments['a']}, {arguments['b']}) = {result}"
            async for event in _stream_text(encoder, message_id, answer):
                yield event

            yield encoder.encode(
                RunFinishedEvent(
                    type=EventType.RUN_FINISHED,
                    thread_id=input_data.thread_id,
                    run_id=input_data.run_id,
                    result={"answer": answer, "tool": tool_name, "arguments": arguments},
                )
            )
        except Exception as exc:
            yield encoder.encode(
                RunErrorEvent(
                    type=EventType.RUN_ERROR,
                    message=str(exc),
                    code=exc.__class__.__name__,
                )
            )

    return StreamingResponse(
        event_generator(),
        media_type=getattr(encoder, "get_content_type", lambda: "text/event-stream")(),
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
