"""
Client demo — uses the Agntcy Directory to discover the CalculatorAgent,
then connects over MCP (streamable-http) and calls its tools.

Discovery flow:
  1. Search the LocalDirectory for an agent named "CalculatorAgent".
  2. Extract the embedded AgentCard from the OASF record.
  3. Read AgentCard.url to get the connection endpoint.
  4. Connect via mcp.ClientSession (streamable-http) and call tools.

NOTE on FastMCP client (agntcy_app_sdk.semantic.fast_mcp):
  The agntcy FastMCPProtocol.create_client() routes tool calls through a
  SLIM/NATS transport, not over HTTP. It cannot replace mcp.ClientSession
  for the plain HTTP transport used here. Use FastMCPProtocol when your
  agent is reachable via a SLIM or NATS broker.

Requires the agent server to be running first:
    python agent.py

Then run this script in a separate terminal:
    python client.py
"""

import asyncio

from mcp.client.streamable_http import streamablehttp_client
from mcp import ClientSession

from directory import directory


async def discover_agent(name: str) -> str:
    """
    Search the directory for an agent by name and return its MCP endpoint URL.
    Raises RuntimeError if no matching agent is found.
    """
    await directory.setup()

    print(f"[Directory] Searching for agent: '{name}' ...")
    results = await directory.search_agent_records(query=name)
    if not results:
        raise RuntimeError(
            f"No agent named '{name}' found in directory. "
            "Is agent.py running?"
        )

    oasf_record = results[0]
    print(f"[Directory] Found: {oasf_record['name']} v{oasf_record['version']}")

    from agntcy_app_sdk.directory.oasf_converter import oasf_to_agent_card
    agent_card = oasf_to_agent_card(oasf_record)
    if agent_card is None:
        raise RuntimeError("Directory record has no A2A AgentCard module.")

    print(f"[Directory] Endpoint: {agent_card.url}")
    print(f"[Directory] Skills  : {[s.name for s in (agent_card.skills or [])]}")
    print()
    return agent_card.url


async def main() -> None:
    print("=== Agntcy Demo — Directory-Driven MCP Client ===\n")

    # ── Step 1: discover the agent via directory ──────────────────────────────
    agent_url = await discover_agent("CalculatorAgent")

    # ── Step 2: connect via mcp.ClientSession (streamable-http) ──────────────
    async with streamablehttp_client(agent_url) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()

            tools_result = await session.list_tools()
            print("Tools available on agent:")
            for tool in tools_result.tools:
                print(f"  • {tool.name}: {tool.description}")
            print()

            result = await session.call_tool("add", {"a": 42, "b": 8})
            print(f"add(42, 8)                     = {result.content[0].text}")

            result = await session.call_tool("multiply", {"a": 6, "b": 7})
            print(f"multiply(6, 7)                 = {result.content[0].text}")

            result = await session.call_tool("celsius_to_fahrenheit", {"celsius": 100})
            print(f"celsius_to_fahrenheit(100 °C)  = {result.content[0].text} °F")


if __name__ == "__main__":
    asyncio.run(main())
