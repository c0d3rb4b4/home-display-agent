#!/bin/bash
# Deployment script for home-display-agent

set -e

echo "Deploying home-display-agent..."

# Navigate to project directory
cd "$(dirname "$0")/.."

# Pull latest changes
git pull origin main

# Build and start services
docker compose build
docker compose up -d

echo "Deployment complete!"
echo "RabbitMQ Management UI: http://localhost:15672"
echo "Default credentials: guest/guest"
