"""Dispatcher service tools.

This module provides tools for job dispatching.

Tools:
    dispatcher_enqueue: Enqueue a display job for processing
    dispatcher_queue_status: Get the current queue status
    dispatcher_job_status: Get the status of a specific job
    dispatcher_cancel: Cancel a pending or running job

These tools communicate with the dispatcher service via HTTP.
"""

# Tool schemas for reference (registered in src/main.py)
DISPATCHER_ENQUEUE_SCHEMA = {
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
}

DISPATCHER_QUEUE_STATUS_SCHEMA = {
    "type": "object",
    "properties": {},
}

DISPATCHER_JOB_STATUS_SCHEMA = {
    "type": "object",
    "properties": {
        "job_id": {
            "type": "string",
            "description": "The job ID to check",
        },
    },
    "required": ["job_id"],
}

DISPATCHER_CANCEL_SCHEMA = {
    "type": "object",
    "properties": {
        "job_id": {
            "type": "string",
            "description": "The job ID to cancel",
        },
    },
    "required": ["job_id"],
}
