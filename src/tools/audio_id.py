"""Audio identification service tools.

This module provides tools for identifying audio content.

Tools:
    audio_identify: Identify audio content from a file or stream
    audio_status: Get the status of an audio identification job

These tools communicate with the audio-id service via HTTP.
"""

# Tool schemas for reference (registered in src/main.py)
AUDIO_IDENTIFY_SCHEMA = {
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
}

AUDIO_STATUS_SCHEMA = {
    "type": "object",
    "properties": {
        "job_id": {
            "type": "string",
            "description": "The job ID to check",
        },
    },
    "required": ["job_id"],
}
