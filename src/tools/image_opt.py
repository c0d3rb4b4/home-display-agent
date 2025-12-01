"""Image optimization service tool for MCP."""

from typing import Any

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

from src.config import Config


def register_image_opt_tools(server: Server, config: Config) -> None:
    """Register image optimization tools with the MCP server."""
    base_url = config.services.image_opt_url

    @server.list_tools()
    async def list_image_tools() -> list[Tool]:
        """List available image optimization tools."""
        return [
            Tool(
                name="image_optimize",
                description="Optimize an image for display",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Path or URL to the image",
                        },
                        "width": {
                            "type": "integer",
                            "description": "Target width in pixels",
                        },
                        "height": {
                            "type": "integer",
                            "description": "Target height in pixels",
                        },
                        "format": {
                            "type": "string",
                            "description": "Output format (jpeg, png, webp)",
                            "enum": ["jpeg", "png", "webp"],
                            "default": "webp",
                        },
                        "quality": {
                            "type": "integer",
                            "description": "Output quality (1-100)",
                            "default": 85,
                        },
                    },
                    "required": ["source"],
                },
            ),
            Tool(
                name="image_info",
                description="Get metadata and info about an image",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "source": {
                            "type": "string",
                            "description": "Path or URL to the image",
                        },
                    },
                    "required": ["source"],
                },
            ),
        ]

    async def image_optimize(
        source: str,
        width: int | None = None,
        height: int | None = None,
        fmt: str = "webp",
        quality: int = 85,
    ) -> dict[str, Any]:
        """Optimize an image for display."""
        async with httpx.AsyncClient() as client:
            payload = {
                "source": source,
                "format": fmt,
                "quality": quality,
            }
            if width:
                payload["width"] = width
            if height:
                payload["height"] = height
            response = await client.post(
                f"{base_url}/optimize",
                json=payload,
                timeout=60.0,
            )
            response.raise_for_status()
            return response.json()

    async def image_info(source: str) -> dict[str, Any]:
        """Get metadata about an image."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/info",
                json={"source": source},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    @server.call_tool()
    async def call_image_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle image tool calls."""
        if name == "image_optimize":
            result = await image_optimize(
                source=arguments["source"],
                width=arguments.get("width"),
                height=arguments.get("height"),
                fmt=arguments.get("format", "webp"),
                quality=arguments.get("quality", 85),
            )
            return [TextContent(type="text", text=str(result))]
        elif name == "image_info":
            result = await image_info(source=arguments["source"])
            return [TextContent(type="text", text=str(result))]
        raise ValueError(f"Unknown image tool: {name}")
