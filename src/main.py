"""Main entry point for the home-display-agent MCP server."""

import asyncio
import logging
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
import httpx

from src.config import load_config, Config

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("home-display-agent")


def create_server(config: Config) -> Server:
    """Create and configure the MCP server with all tools."""
    server = Server("home-display-agent")

    # Tool definitions
    TOOLS = [
        # Audio ID tools
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
        # Image optimization tools
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
        # Overlay tools
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
        # Dispatcher tools
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
        # Monitor tools
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

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        """List all available tools."""
        return TOOLS

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        """Handle tool calls."""
        try:
            result = await _execute_tool(name, arguments, config)
            return [TextContent(type="text", text=str(result))]
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Error executing tool {name}: {str(e)}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]

    return server


async def _execute_tool(name: str, arguments: dict, config: Config) -> dict[str, Any]:
    """Execute a tool and return the result."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Audio ID tools
        if name == "audio_identify":
            response = await client.post(
                f"{config.services.audio_id_url}/identify",
                json={
                    "source": arguments["source"],
                    "duration": arguments.get("duration", 10),
                },
            )
            response.raise_for_status()
            return response.json()

        elif name == "audio_status":
            response = await client.get(
                f"{config.services.audio_id_url}/status/{arguments['job_id']}",
            )
            response.raise_for_status()
            return response.json()

        # Image optimization tools
        elif name == "image_optimize":
            payload = {
                "source": arguments["source"],
                "format": arguments.get("format", "webp"),
                "quality": arguments.get("quality", 85),
            }
            if "width" in arguments:
                payload["width"] = arguments["width"]
            if "height" in arguments:
                payload["height"] = arguments["height"]
            response = await client.post(
                f"{config.services.image_opt_url}/optimize",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

        elif name == "image_info":
            response = await client.post(
                f"{config.services.image_opt_url}/info",
                json={"source": arguments["source"]},
            )
            response.raise_for_status()
            return response.json()

        # Overlay tools
        elif name == "overlay_create":
            response = await client.post(
                f"{config.services.overlay_url}/create",
                json={
                    "template": arguments["template"],
                    "data": arguments["data"],
                    "width": arguments.get("width", 1920),
                    "height": arguments.get("height", 1080),
                },
            )
            response.raise_for_status()
            return response.json()

        elif name == "overlay_list_templates":
            response = await client.get(
                f"{config.services.overlay_url}/templates",
            )
            response.raise_for_status()
            return response.json()

        elif name == "overlay_preview":
            response = await client.post(
                f"{config.services.overlay_url}/preview",
                json={
                    "template": arguments["template"],
                    "data": arguments["data"],
                },
            )
            response.raise_for_status()
            return response.json()

        # Dispatcher tools
        elif name == "dispatcher_enqueue":
            payload = {
                "job_type": arguments["job_type"],
                "source": arguments["source"],
                "priority": arguments.get("priority", 5),
            }
            if "options" in arguments:
                payload["options"] = arguments["options"]
            response = await client.post(
                f"{config.services.dispatcher_url}/enqueue",
                json=payload,
            )
            response.raise_for_status()
            return response.json()

        elif name == "dispatcher_queue_status":
            response = await client.get(
                f"{config.services.dispatcher_url}/queue/status",
            )
            response.raise_for_status()
            return response.json()

        elif name == "dispatcher_job_status":
            response = await client.get(
                f"{config.services.dispatcher_url}/job/{arguments['job_id']}",
            )
            response.raise_for_status()
            return response.json()

        elif name == "dispatcher_cancel":
            response = await client.delete(
                f"{config.services.dispatcher_url}/job/{arguments['job_id']}",
            )
            response.raise_for_status()
            return response.json()

        # Monitor tools
        elif name == "monitor_health":
            response = await client.get(
                f"{config.services.monitor_url}/health",
            )
            response.raise_for_status()
            return response.json()

        elif name == "monitor_stream_status":
            response = await client.get(
                f"{config.services.monitor_url}/stream/status",
            )
            response.raise_for_status()
            return response.json()

        elif name == "monitor_failures":
            params = {"limit": arguments.get("limit", 10)}
            if "service" in arguments:
                params["service"] = arguments["service"]
            response = await client.get(
                f"{config.services.monitor_url}/failures",
                params=params,
            )
            response.raise_for_status()
            return response.json()

        elif name == "monitor_metrics":
            response = await client.get(
                f"{config.services.monitor_url}/metrics",
                params={"period": arguments.get("period", "1h")},
            )
            response.raise_for_status()
            return response.json()

        else:
            raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Run the MCP server."""
    config = load_config()
    logger.info(f"Starting home-display-agent MCP server (log level: {config.log_level})")
    logging.getLogger().setLevel(config.log_level)

    server = create_server(config)

    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
