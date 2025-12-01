"""Image optimization service tools.

This module provides tools for optimizing images.

Tools:
    image_optimize: Optimize an image for display
    image_info: Get metadata and info about an image

These tools communicate with the image-opt service via HTTP.
"""

# Tool schemas for reference (registered in src/main.py)
IMAGE_OPTIMIZE_SCHEMA = {
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
}

IMAGE_INFO_SCHEMA = {
    "type": "object",
    "properties": {
        "source": {
            "type": "string",
            "description": "Path or URL to the image",
        },
    },
    "required": ["source"],
}
