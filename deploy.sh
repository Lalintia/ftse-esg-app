#!/bin/bash
# Deploy FTSE ESG Web App

set -e

echo "Building containers..."
docker compose build

echo "Starting services..."
docker compose up -d

echo ""
echo "Deployed! Check http://localhost"
echo "View logs: docker compose logs -f"
