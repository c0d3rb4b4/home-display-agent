#!/bin/bash
# View logs for all services

set -e

cd "$(dirname "$0")/.."

docker compose logs -f "$@"
