"""
CalculatorAgent — FastMCP server built with agntcy-app-sdk.

Run:
    python agent.py
"""

import asyncio

from mcp.server.fastmcp import FastMCP

from directory import directory
from oasf_record import calculator_record

AGENT_URL = "http://localhost:8000/mcp"

mcp = FastMCP(
    name=calculator_record.name,
    instructions=calculator_record.description,
    host="127.0.0.1",
    port=8000,
)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Add two numbers together."""
    return a + b


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b


@mcp.tool()
def celsius_to_fahrenheit(celsius: float) -> float:
    """Convert a temperature from Celsius to Fahrenheit."""
    return celsius * 9 / 5 + 32


if __name__ == "__main__":
    async def register() -> str:
        await directory.setup()
        agent_card = calculator_record.to_agent_card(url=AGENT_URL)
        cid = await directory.push_agent_record(agent_card)
        return cid

    print(f"Starting {calculator_record.name} v{calculator_record.version}")
    print(f"Domain   : {calculator_record.domain} / {calculator_record.category}")
    print(f"Skills   : {[s.name for s in calculator_record.skills]}")
    print()

    cid = asyncio.run(register())
    print(f"[Directory] Record pushed -> CID: {cid}")
    print(f"[Directory] Agent discoverable by name: '{calculator_record.name}'")
    print()
    print(f"Server listening on {AGENT_URL}  (Ctrl+C to stop)")
    mcp.run(transport="streamable-http")
