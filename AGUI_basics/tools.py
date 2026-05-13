"""Shared math tools used by the MCP and AG-UI examples."""

from __future__ import annotations


async def add(a: float, b: float) -> float:
    result = a + b
    print(f"[tools.add] called with a={a}, b={b}, result={result}", flush=True)
    return result


async def subtract(a: float, b: float) -> float:
    result = a - b
    print(f"[tools.subtract] called with a={a}, b={b}, result={result}", flush=True)
    return result


TOOLS = {
    "add": add,
    "subtract": subtract,
}


TOOL_DEFINITIONS = [
    {
        "name": "add",
        "description": "Add two numbers.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number."},
                "b": {"type": "number", "description": "The second number."},
            },
            "required": ["a", "b"],
        },
    },
    {
        "name": "subtract",
        "description": "Subtract b from a.",
        "parameters": {
            "type": "object",
            "properties": {
                "a": {"type": "number", "description": "The first number."},
                "b": {"type": "number", "description": "The number to subtract."},
            },
            "required": ["a", "b"],
        },
    },
]
