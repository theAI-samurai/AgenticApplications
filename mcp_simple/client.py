import asyncio
from fastmcp import Client

client = Client("http://0.0.0.0:8000/mcp")

async def call_tool(tool_name, tool_data):
    async with client:
        result = await client.call_tool(tool_name, tool_data)
        print(result)

asyncio.run(call_tool("add", {"a": 10, "b": 5}))
print("=" * 50)
asyncio.run(call_tool("subtract", {"a": 10, "b": 5}))
print("=" * 50)