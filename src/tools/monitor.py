"""Monitor service tools.

This module provides tools for system monitoring.

Tools:
    monitor_health: Check the health status of all services
    monitor_stream_status: Get the current stream/display status
    monitor_failures: Get recent failures and errors
    monitor_metrics: Get system metrics and statistics

These tools communicate with the monitor service via HTTP.
"""

# Tool schemas for reference (registered in src/main.py)
MONITOR_HEALTH_SCHEMA = {
    "type": "object",
    "properties": {},
}

MONITOR_STREAM_STATUS_SCHEMA = {
    "type": "object",
    "properties": {},
}

MONITOR_FAILURES_SCHEMA = {
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
}

MONITOR_METRICS_SCHEMA = {
    "type": "object",
    "properties": {
        "period": {
            "type": "string",
            "description": "Time period for metrics",
            "enum": ["1h", "6h", "24h", "7d"],
            "default": "1h",
        },
    },
}
