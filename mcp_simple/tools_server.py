from fastmcp import FastMCP
import uvicorn
from starlette.responses import JSONResponse


mcp = FastMCP("math-tools")
app = mcp.http_app()

# ---------------------- Health and Readiness Checks Functions ----------------------

async def health_check(_request):
    return JSONResponse(status_code=200, content=200)


async def ready_check(_request):
    return JSONResponse(status_code=200, content=200)

# ---------------------- MCP Tools ----------------------

@mcp.tool()
async def add(a: float, b: float) -> float:
	return a + b

@mcp.tool()
async def subtract(a: float, b: float) -> float:
	return a - b

app.add_route("/health", health_check, methods=["GET"])
app.add_route("/ready", ready_check, methods=["GET"])


if __name__ == "__main__":
	uvicorn.run(app, host="0.0.0.0", port=8000)
	
