"""Streamlit client for the local AG-UI basics server."""

from __future__ import annotations

import json
import uuid
from typing import Any

import httpx
import streamlit as st


DEFAULT_ENDPOINT = "http://localhost:8001/"


def _event_value(event: dict[str, Any], snake: str, camel: str | None = None) -> Any:
    return event.get(snake, event.get(camel or snake))


def _run_payload(prompt: str, thread_id: str) -> dict[str, Any]:
    return {
        "threadId": thread_id,
        "runId": f"run_{uuid.uuid4().hex}",
        "state": st.session_state.get("agent_state", {}),
        "messages": [
            {
                "id": f"user_{uuid.uuid4().hex}",
                "role": "user",
                "content": prompt,
            }
        ],
        "tools": [
            {
                "name": "add",
                "description": "Add two numbers.",
                "parameters": {
                    "type": "object",
                    "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                    "required": ["a", "b"],
                },
            },
            {
                "name": "subtract",
                "description": "Subtract b from a.",
                "parameters": {
                    "type": "object",
                    "properties": {"a": {"type": "number"}, "b": {"type": "number"}},
                    "required": ["a", "b"],
                },
            },
        ],
        "context": [],
        "forwardedProps": {},
    }


def stream_agui(endpoint: str, prompt: str, thread_id: str) -> tuple[str, list[dict[str, Any]]]:
    answer = ""
    events: list[dict[str, Any]] = []

    with httpx.stream(
        "POST",
        endpoint,
        json=_run_payload(prompt, thread_id),
        headers={"Accept": "text/event-stream"},
        timeout=30.0,
    ) as response:
        response.raise_for_status()
        for line in response.iter_lines():
            if not line or not line.startswith("data:"):
                continue
            event = json.loads(line.removeprefix("data:").strip())
            events.append(event)

            event_type = event.get("type")
            if event_type == "TEXT_MESSAGE_CONTENT":
                answer += str(_event_value(event, "delta"))
            elif event_type == "STATE_SNAPSHOT":
                st.session_state.agent_state = _event_value(event, "snapshot") or {}
            elif event_type == "STATE_DELTA":
                for patch in _event_value(event, "delta") or []:
                    path = patch.get("path", "").lstrip("/")
                    if path:
                        st.session_state.agent_state[path] = patch.get("value")

    return answer, events


st.set_page_config(page_title="AG-UI Basics", page_icon="AG", layout="wide")
st.title("AG-UI Basics")

if "thread_id" not in st.session_state:
    st.session_state.thread_id = f"thread_{uuid.uuid4().hex}"
if "messages" not in st.session_state:
    st.session_state.messages = []
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {}
if "last_events" not in st.session_state:
    st.session_state.last_events = []

with st.sidebar:
    endpoint = st.text_input("AG-UI endpoint", DEFAULT_ENDPOINT)
    st.json(st.session_state.agent_state)

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

prompt = st.chat_input("Try: add 10 and 5, or subtract 10 from 5")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        try:
            answer, events = stream_agui(endpoint, prompt, st.session_state.thread_id)
            placeholder.write(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.last_events = events
        except Exception as exc:
            placeholder.error(str(exc))

with st.expander("Last AG-UI events", expanded=False):
    st.json(st.session_state.last_events)
