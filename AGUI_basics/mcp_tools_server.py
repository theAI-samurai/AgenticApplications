"""FastMCP copy of the simple math tools for side-by-side comparison."""

from __future__ import annotations

import uvicorn
from fastmcp import FastMCP
from starlette.responses import JSONResponse

from tools import add as add_tool
from tools import subtract as subtract_tool


mcp = FastMCP("math-tools")
app = mcp.http_app()


async def health_check(_request):
    return JSONResponse(status_code=200, content=200)


async def ready_check(_request):
    return JSONResponse(status_code=200, content=200)


@mcp.tool()
async def add(a: float, b: float) -> float:
    return await add_tool(a, b)


@mcp.tool()
async def subtract(a: float, b: float) -> float:
    return await subtract_tool(a, b)


app.add_route("/health", health_check, methods=["GET"])
app.add_route("/ready", ready_check, methods=["GET"])


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
