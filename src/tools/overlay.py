"""Overlay generation service tools.

This module provides tools for generating overlay images.

Tools:
    overlay_create: Create an overlay image with text and graphics
    overlay_list_templates: List available overlay templates
    overlay_preview: Generate a preview of an overlay

These tools communicate with the overlay service via HTTP.
"""

# Tool schemas for reference (registered in src/main.py)
OVERLAY_CREATE_SCHEMA = {
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
}

OVERLAY_LIST_TEMPLATES_SCHEMA = {
    "type": "object",
    "properties": {},
}

OVERLAY_PREVIEW_SCHEMA = {
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
}
