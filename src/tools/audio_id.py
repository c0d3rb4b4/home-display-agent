"""Audio identification service tool for MCP."""

from typing import Any

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

from src.config import Config


def register_audio_id_tools(server: Server, config: Config) -> None:
    """Register audio identification tools with the MCP server."""
    base_url = config.services.audio_id_url

    @server.list_tools()
    async def list_audio_tools() -> list[Tool]:
        """List available audio identification tools."""
        return [
            Tool(
                name="audio_identify",
                description="Identify audio content from a file or stream",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Path or URL to the audio source",
                        },
                        "duration": {
                            "type": "integer",
                            "description": "Duration in seconds to analyze",
                            "default": 10,
                        },
                    },
                    "required": ["source"],
                },
            ),
            Tool(
                name="audio_status",
                description="Get the status of an audio identification job",
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
        ]

    async def audio_identify(source: str, duration: int = 10) -> dict[str, Any]:
        """Identify audio content from a source."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/identify",
                json={"source": source, "duration": duration},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def audio_status(job_id: str) -> dict[str, Any]:
        """Get the status of an audio identification job."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/status/{job_id}",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    @server.call_tool()
    async def call_audio_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle audio tool calls."""
        if name == "audio_identify":
            result = await audio_identify(
                source=arguments["source"],
                duration=arguments.get("duration", 10),
            )
            return [TextContent(type="text", text=str(result))]
        elif name == "audio_status":
            result = await audio_status(job_id=arguments["job_id"])
            return [TextContent(type="text", text=str(result))]
        raise ValueError(f"Unknown audio tool: {name}")
