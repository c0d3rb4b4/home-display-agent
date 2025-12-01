# home-display-agent

MCP agent that exposes tools to control/query the whole system: enqueue display jobs, generate overlays via APIs, query stream status, and inspect failures, so an LLM client can orchestrate everything.

## Project Structure

```
home-display-agent/
├── src/
│   ├── __init__.py
│   ├── main.py              # MCP server entry point
│   ├── config.py            # Configuration management
│   └── tools/
│       ├── __init__.py
│       ├── audio_id.py      # Audio identification tools
│       ├── image_opt.py     # Image optimization tools
│       ├── overlay.py       # Overlay generation tools
│       ├── dispatcher.py    # Job dispatcher tools
│       └── monitor.py       # Monitoring tools
├── config/
│   └── default.env          # Default configuration
├── deploy/
│   ├── deploy.sh            # Deployment script
│   ├── stop.sh              # Stop services
│   └── logs.sh              # View logs
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## MCP Server Configuration

Add this configuration to your MCP client (e.g., Claude Desktop):

### Using Docker

```json
{
  "mcpServers": {
    "home-display-agent": {
      "command": "docker",
      "args": [
        "run",
        "--rm",
        "-i",
        "--network", "home-display-agent_home-display-network",
        "-e", "AUDIO_ID_URL=http://audio-id:8000",
        "-e", "IMAGE_OPT_URL=http://image-opt:8000",
        "-e", "OVERLAY_URL=http://overlay:8000",
        "-e", "DISPATCHER_URL=http://dispatcher:8000",
        "-e", "MONITOR_URL=http://monitor:8000",
        "home-display-agent"
      ]
    }
  }
}
```

### Using Python directly

```json
{
  "mcpServers": {
    "home-display-agent": {
      "command": "python",
      "args": ["-m", "src.main"],
      "cwd": "/path/to/home-display-agent",
      "env": {
        "AUDIO_ID_URL": "http://localhost:8001",
        "IMAGE_OPT_URL": "http://localhost:8002",
        "OVERLAY_URL": "http://localhost:8003",
        "DISPATCHER_URL": "http://localhost:8004",
        "MONITOR_URL": "http://localhost:8005"
      }
    }
  }
}
```

## Available Tools

### Audio Identification
- `audio_identify` - Identify audio content from a file or stream
- `audio_status` - Get the status of an audio identification job

### Image Optimization
- `image_optimize` - Optimize an image for display (resize, format, quality)
- `image_info` - Get metadata and info about an image

### Overlay Generation
- `overlay_create` - Create an overlay image with text and graphics
- `overlay_list_templates` - List available overlay templates
- `overlay_preview` - Generate a preview of an overlay

### Dispatcher
- `dispatcher_enqueue` - Enqueue a display job for processing
- `dispatcher_queue_status` - Get the current queue status
- `dispatcher_job_status` - Get the status of a specific job
- `dispatcher_cancel` - Cancel a pending or running job

### Monitor
- `monitor_health` - Check the health status of all services
- `monitor_stream_status` - Get the current stream/display status
- `monitor_failures` - Get recent failures and errors
- `monitor_metrics` - Get system metrics and statistics

## Docker Compose Services

The `docker-compose.yml` includes:

- **home-display-agent**: The MCP server
- **rabbitmq**: RabbitMQ 3 with management UI (ports 5672, 15672)
- **samba**: Samba file server for media storage (ports 139, 445)

## Deployment

### Quick Start

```bash
# Clone the repository
git clone https://github.com/c0d3rb4b4/home-display-agent.git
cd home-display-agent

# Build and start services
docker compose build
docker compose up -d

# View logs
docker compose logs -f
```

### Using Deployment Scripts

```bash
# Deploy
./deploy/deploy.sh

# View logs
./deploy/logs.sh

# Stop services
./deploy/stop.sh
```

### GitHub Actions Workflow

The repository includes a GitHub Actions workflow (`.github/workflows/deploy.yml`) that automatically builds and deploys on push to the `main` branch using a self-hosted runner.

## Configuration

Configuration is done via environment variables. See `config/default.env` for available options:

| Variable | Default | Description |
|----------|---------|-------------|
| `AUDIO_ID_URL` | `http://audio-id:8000` | Audio identification service URL |
| `IMAGE_OPT_URL` | `http://image-opt:8000` | Image optimization service URL |
| `OVERLAY_URL` | `http://overlay:8000` | Overlay generation service URL |
| `DISPATCHER_URL` | `http://dispatcher:8000` | Dispatcher service URL |
| `MONITOR_URL` | `http://monitor:8000` | Monitor service URL |
| `RABBITMQ_HOST` | `rabbitmq` | RabbitMQ host |
| `RABBITMQ_PORT` | `5672` | RabbitMQ port |
| `RABBITMQ_USER` | `guest` | RabbitMQ username |
| `RABBITMQ_PASSWORD` | `guest` | RabbitMQ password |
| `SAMBA_HOST` | `samba` | Samba server host |
| `SAMBA_SHARE` | `media` | Samba share name |
| `LOG_LEVEL` | `INFO` | Logging level |

## Development

### Requirements

- Python 3.12+
- Docker and Docker Compose

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run the MCP server locally
python -m src.main
```

## License

MIT
