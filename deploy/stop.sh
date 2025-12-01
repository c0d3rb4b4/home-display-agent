#!/bin/bash
# Stop all services

set -e

echo "Stopping home-display-agent..."

cd "$(dirname "$0")/.."

docker compose down

echo "Services stopped."
