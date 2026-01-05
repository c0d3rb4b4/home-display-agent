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
        logger.info("Tool invoked: name=%s, arguments=%s", name, arguments)
        try:
            result = await _execute_tool(name, arguments, config)
            logger.debug("Tool execution successful: name=%s, result_keys=%s", name, list(result.keys()) if isinstance(result, dict) else type(result).__name__)
            return [TextContent(type="text", text=str(result))]
        except httpx.HTTPStatusError as e:
            error_msg = f"HTTP error: {e.response.status_code} - {e.response.text}"
            logger.error("HTTP error during tool execution: tool=%s, status=%d, url=%s, response=%s",
                        name, e.response.status_code, e.request.url, e.response.text)
            return [TextContent(type="text", text=error_msg)]
        except httpx.RequestError as e:
            error_msg = f"Request error: {str(e)}"
            logger.error("Network error during tool execution: tool=%s, error=%s", name, str(e), exc_info=True)
            return [TextContent(type="text", text=error_msg)]
        except Exception as e:
            error_msg = f"Error executing tool {name}: {str(e)}"
            logger.error("Unexpected error during tool execution: tool=%s, error=%s", name, str(e), exc_info=True)
            return [TextContent(type="text", text=error_msg)]

    return server


async def _execute_tool(name: str, arguments: dict, config: Config) -> dict[str, Any]:
    """Execute a tool and return the result."""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Audio ID tools
        if name == "audio_identify":
            url = f"{config.services.audio_id_url}/identify"
            payload = {
                "source": arguments["source"],
                "duration": arguments.get("duration", 10),
            }
            logger.info("Requesting audio identification: url=%s, source=%s, duration=%d",
                       url, arguments["source"], payload["duration"])
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info("Audio identification complete: source=%s, status=%d", arguments["source"], response.status_code)
            return result

        elif name == "audio_status":
            url = f"{config.services.audio_id_url}/status/{arguments['job_id']}"
            logger.debug("Checking audio identification status: url=%s, job_id=%s", url, arguments['job_id'])
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            logger.debug("Audio status retrieved: job_id=%s, status=%d", arguments['job_id'], response.status_code)
            return result

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
            url = f"{config.services.image_opt_url}/optimize"
            logger.info("Requesting image optimization: url=%s, source=%s, format=%s, quality=%d, dimensions=%sx%s",
                       url, arguments["source"], payload["format"], payload["quality"],
                       payload.get("width", "auto"), payload.get("height", "auto"))
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info("Image optimization complete: source=%s, status=%d", arguments["source"], response.status_code)
            return result

        elif name == "image_info":
            url = f"{config.services.image_opt_url}/info"
            logger.debug("Requesting image info: url=%s, source=%s", url, arguments["source"])
            response = await client.post(url, json={"source": arguments["source"]})
            response.raise_for_status()
            result = response.json()
            logger.debug("Image info retrieved: source=%s, status=%d", arguments["source"], response.status_code)
            return result

        # Overlay tools
        elif name == "overlay_create":
            payload = {
                "template": arguments["template"],
                "data": arguments["data"],
                "width": arguments.get("width", 1920),
                "height": arguments.get("height", 1080),
            }
            url = f"{config.services.overlay_url}/create"
            logger.info("Requesting overlay creation: url=%s, template=%s, dimensions=%dx%d, data_keys=%s",
                       url, arguments["template"], payload["width"], payload["height"],
                       list(arguments["data"].keys()) if isinstance(arguments["data"], dict) else "unknown")
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info("Overlay creation complete: template=%s, status=%d", arguments["template"], response.status_code)
            return result

        elif name == "overlay_list_templates":
            url = f"{config.services.overlay_url}/templates"
            logger.debug("Requesting overlay templates list: url=%s", url)
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            template_count = len(result) if isinstance(result, list) else "unknown"
            logger.debug("Overlay templates retrieved: count=%s, status=%d", template_count, response.status_code)
            return result

        elif name == "overlay_preview":
            payload = {
                "template": arguments["template"],
                "data": arguments["data"],
            }
            url = f"{config.services.overlay_url}/preview"
            logger.debug("Requesting overlay preview: url=%s, template=%s", url, arguments["template"])
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.debug("Overlay preview complete: template=%s, status=%d", arguments["template"], response.status_code)
            return result

        # Dispatcher tools
        elif name == "dispatcher_enqueue":
            payload = {
                "job_type": arguments["job_type"],
                "source": arguments["source"],
                "priority": arguments.get("priority", 5),
            }
            if "options" in arguments:
                payload["options"] = arguments["options"]
            url = f"{config.services.dispatcher_url}/enqueue"
            logger.info("Enqueueing job: url=%s, job_type=%s, source=%s, priority=%d",
                       url, payload["job_type"], payload["source"], payload["priority"])
            response = await client.post(url, json=payload)
            response.raise_for_status()
            result = response.json()
            logger.info("Job enqueued: job_type=%s, status=%d", payload["job_type"], response.status_code)
            return result

        elif name == "dispatcher_queue_status":
            url = f"{config.services.dispatcher_url}/queue/status"
            logger.debug("Requesting queue status: url=%s", url)
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            logger.debug("Queue status retrieved: status=%d", response.status_code)
            return result

        elif name == "dispatcher_job_status":
            url = f"{config.services.dispatcher_url}/job/{arguments['job_id']}"
            logger.debug("Checking job status: url=%s, job_id=%s", url, arguments['job_id'])
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            logger.debug("Job status retrieved: job_id=%s, status=%d", arguments['job_id'], response.status_code)
            return result

        elif name == "dispatcher_cancel":
            url = f"{config.services.dispatcher_url}/job/{arguments['job_id']}"
            logger.info("Cancelling job: url=%s, job_id=%s", url, arguments['job_id'])
            response = await client.delete(url)
            response.raise_for_status()
            result = response.json()
            logger.info("Job cancelled: job_id=%s, status=%d", arguments['job_id'], response.status_code)
            return result

        # Monitor tools
        elif name == "monitor_health":
            url = f"{config.services.monitor_url}/health"
            logger.debug("Requesting system health: url=%s", url)
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            logger.debug("System health retrieved: status=%d", response.status_code)
            return result

        elif name == "monitor_stream_status":
            url = f"{config.services.monitor_url}/stream/status"
            logger.debug("Requesting stream status: url=%s", url)
            response = await client.get(url)
            response.raise_for_status()
            result = response.json()
            logger.debug("Stream status retrieved: status=%d", response.status_code)
            return result

        elif name == "monitor_failures":
            params = {"limit": arguments.get("limit", 10)}
            if "service" in arguments:
                params["service"] = arguments["service"]
            url = f"{config.services.monitor_url}/failures"
            logger.debug("Requesting failures: url=%s, limit=%d, service=%s",
                        url, params["limit"], params.get("service", "all"))
            response = await client.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            failure_count = len(result) if isinstance(result, list) else "unknown"
            logger.debug("Failures retrieved: count=%s, status=%d", failure_count, response.status_code)
            return result

        elif name == "monitor_metrics":
            params = {"period": arguments.get("period", "1h")}
            url = f"{config.services.monitor_url}/metrics"
            logger.debug("Requesting metrics: url=%s, period=%s", url, params["period"])
            response = await client.get(url, params=params)
            response.raise_for_status()
            result = response.json()
            logger.debug("Metrics retrieved: period=%s, status=%d", params["period"], response.status_code)
            return result

        else:
            raise ValueError(f"Unknown tool: {name}")


async def main() -> None:
    """Run the MCP server."""
    config = load_config()
    logger.info("Starting home-display-agent MCP server: log_level=%s", config.log_level)
    logger.info("Service URLs: audio_id=%s, image_opt=%s, overlay=%s, dispatcher=%s, monitor=%s",
               config.services.audio_id_url, config.services.image_opt_url, config.services.overlay_url,
               config.services.dispatcher_url, config.services.monitor_url)
    logging.getLogger().setLevel(config.log_level)

    server = create_server(config)
    logger.debug("MCP server created and configured")

    async with stdio_server() as (read_stream, write_stream):
        logger.info("Starting stdio server for MCP communication")
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )


if __name__ == "__main__":
    asyncio.run(main())
