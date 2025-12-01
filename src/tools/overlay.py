"""Overlay generation service tool for MCP."""

from typing import Any

import httpx
from mcp.server import Server
from mcp.types import Tool, TextContent

from src.config import Config


def register_overlay_tools(server: Server, config: Config) -> None:
    """Register overlay generation tools with the MCP server."""
    base_url = config.services.overlay_url

    @server.list_tools()
    async def list_overlay_tools() -> list[Tool]:
        """List available overlay tools."""
        return [
            Tool(
                name="overlay_create",
                description="Create an overlay image with text and graphics",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template": {
                            "type": "string",
                            "description": "Template name to use",
                        },
                        "data": {
                            "type": "object",
                            "description": "Data to populate the template",
                        },
                        "width": {
                            "type": "integer",
                            "description": "Overlay width in pixels",
                            "default": 1920,
                        },
                        "height": {
                            "type": "integer",
                            "description": "Overlay height in pixels",
                            "default": 1080,
                        },
                    },
                    "required": ["template", "data"],
                },
            ),
            Tool(
                name="overlay_list_templates",
                description="List available overlay templates",
                inputSchema={
                    "type": "object",
                    "properties": {},
                },
            ),
            Tool(
                name="overlay_preview",
                description="Generate a preview of an overlay",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template": {
                            "type": "string",
                            "description": "Template name to use",
                        },
                        "data": {
                            "type": "object",
                            "description": "Data to populate the template",
                        },
                    },
                    "required": ["template", "data"],
                },
            ),
        ]

    async def overlay_create(
        template: str,
        data: dict[str, Any],
        width: int = 1920,
        height: int = 1080,
    ) -> dict[str, Any]:
        """Create an overlay image."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/create",
                json={
                    "template": template,
                    "data": data,
                    "width": width,
                    "height": height,
                },
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    async def overlay_list_templates() -> dict[str, Any]:
        """List available overlay templates."""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/templates",
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()

    async def overlay_preview(
        template: str,
        data: dict[str, Any],
    ) -> dict[str, Any]:
        """Generate a preview of an overlay."""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{base_url}/preview",
                json={"template": template, "data": data},
                timeout=30.0,
            )
            response.raise_for_status()
            return response.json()

    @server.call_tool()
    async def call_overlay_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle overlay tool calls."""
        if name == "overlay_create":
            result = await overlay_create(
                template=arguments["template"],
                data=arguments["data"],
                width=arguments.get("width", 1920),
                height=arguments.get("height", 1080),
            )
            return [TextContent(type="text", text=str(result))]
        elif name == "overlay_list_templates":
            result = await overlay_list_templates()
            return [TextContent(type="text", text=str(result))]
        elif name == "overlay_preview":
            result = await overlay_preview(
                template=arguments["template"],
                data=arguments["data"],
            )
            return [TextContent(type="text", text=str(result))]
        raise ValueError(f"Unknown overlay tool: {name}")
