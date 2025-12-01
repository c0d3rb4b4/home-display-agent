"""Dispatcher service tool for MCP."""

from typing import Any

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

from src.config import Config


def register_dispatcher_tools(server: Server, config: Config) -> None:
    """Register dispatcher tools with the MCP server."""
    base_url = config.services.dispatcher_url

    @server.list_tools()
    async def list_dispatcher_tools() -> list[Tool]:
        """List available dispatcher tools."""
        return [
            Tool(
                name="dispatcher_enqueue",
                description="Enqueue a display job for processing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_type": {
                            "type": "string",
                            "description": "Type of job (image, video, slideshow)",
                            "enum": ["image", "video", "slideshow"],
                        },
                        "source": {
                            "type": "string",
                            "description": "Path or URL to the content",
                        },
                        "priority": {
                            "type": "integer",
                            "description": "Job priority (higher = more urgent)",
                            "default": 5,
                        },
                        "options": {
                            "type": "object",
                            "description": "Additional job options",
                        },
                    },
                    "required": ["job_type", "source"],
                },
            ),
            Tool(
                name="dispatcher_queue_status",
                description="Get the current queue status",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="dispatcher_job_status",
                description="Get the status of a specific job",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "The job ID to check",
                        },
                    },
                    "required": ["job_id"],
                },
            ),
            Tool(
                name="dispatcher_cancel",
                description="Cancel a pending or running job",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "job_id": {
                            "type": "string",
                            "description": "The job ID to cancel",
                        },
                    },
                    "required": ["job_id"],
                },
            ),
        ]

    async def dispatcher_enqueue(
        job_type: str,
        source: str,
        priority: int = 5,
        options: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Enqueue a display job."""
        async with httpx.AsyncClient() as client:
            payload = {
                "job_type": job_type,
                "source": source,
                "priority": priority,
            }
            if options:
                payload["options"] = options
            response = await client.post(
                f"{base_url}/enqueue",
                json=payload,
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def dispatcher_queue_status() -> dict[str, Any]:
        """Get the current queue status."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/queue/status",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def dispatcher_job_status(job_id: str) -> dict[str, Any]:
        """Get the status of a specific job."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/job/{job_id}",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def dispatcher_cancel(job_id: str) -> dict[str, Any]:
        """Cancel a pending or running job."""
        async with httpx.AsyncClient() as client:
            response = await client.delete(
                f"{base_url}/job/{job_id}",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    @server.call_tool()
    async def call_dispatcher_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle dispatcher tool calls."""
        if name == "dispatcher_enqueue":
            result = await dispatcher_enqueue(
                job_type=arguments["job_type"],
                source=arguments["source"],
                priority=arguments.get("priority", 5),
                options=arguments.get("options"),
            )
            return [TextContent(type="text", text=str(result))]
        elif name == "dispatcher_queue_status":
            result = await dispatcher_queue_status()
            return [TextContent(type="text", text=str(result))]
        elif name == "dispatcher_job_status":
            result = await dispatcher_job_status(job_id=arguments["job_id"])
            return [TextContent(type="text", text=str(result))]
        elif name == "dispatcher_cancel":
            result = await dispatcher_cancel(job_id=arguments["job_id"])
            return [TextContent(type="text", text=str(result))]
        raise ValueError(f"Unknown dispatcher tool: {name}")
