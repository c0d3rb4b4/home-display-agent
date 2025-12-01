"""Monitor service tool for MCP."""

from typing import Any

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

from src.config import Config


def register_monitor_tools(server: Server, config: Config) -> None:
    """Register monitoring tools with the MCP server."""
    base_url = config.services.monitor_url

    @server.list_tools()
    async def list_monitor_tools() -> list[Tool]:
        """List available monitoring tools."""
        return [
            Tool(
                name="monitor_health",
                description="Check the health status of all services",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="monitor_stream_status",
                description="Get the current stream/display status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="monitor_failures",
                description="Get recent failures and errors",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of failures to return",
                            "default": 10,
                        },
                        "service": {
                            "type": "string",
                            "description": "Filter by service name",
                        },
                    },
                },
            ),
            Tool(
                name="monitor_metrics",
                description="Get system metrics and statistics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "period": {
                            "type": "string",
                            "description": "Time period for metrics",
                            "enum": ["1h", "6h", "24h", "7d"],
                            "default": "1h",
                        },
                    },
                },
            ),
        ]

    async def monitor_health() -> dict[str, Any]:
        """Check the health status of all services."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/health",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def monitor_stream_status() -> dict[str, Any]:
        """Get the current stream/display status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/stream/status",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def monitor_failures(
        limit: int = 10,
        service: str | None = None,
    ) -> dict[str, Any]:
        """Get recent failures and errors."""
        async with httpx.AsyncClient() as client:
            params = {"limit": limit}
            if service:
                params["service"] = service
            response = await client.get(
                f"{base_url}/failures",
                params=params,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def monitor_metrics(period: str = "1h") -> dict[str, Any]:
        """Get system metrics and statistics."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/metrics",
                params={"period": period},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    @server.call_tool()
    async def call_monitor_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle monitoring tool calls."""
        if name == "monitor_health":
            result = await monitor_health()
            return [TextContent(type="text", text=str(result))]
        elif name == "monitor_stream_status":
            result = await monitor_stream_status()
            return [TextContent(type="text", text=str(result))]
        elif name == "monitor_failures":
            result = await monitor_failures(
                limit=arguments.get("limit", 10),
                service=arguments.get("service"),
            )
            return [TextContent(type="text", text=str(result))]
        elif name == "monitor_metrics":
            result = await monitor_metrics(period=arguments.get("period", "1h"))
            return [TextContent(type="text", text=str(result))]
        raise ValueError(f"Unknown monitor tool: {name}")
