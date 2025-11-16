#!/usr/bin/env bash
# start_all.sh — simple wrapper to start both services in background and write logs to ./logs
# Usage: bash scripts/start_all.sh

set -euo pipefail
ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT_DIR"

mkdir -p logs

# Start product-service in background
echo "Starting product-service (logs -> logs/product.log)..."
(cd product-service && nohup go run main.go > "$ROOT_DIR/logs/product.log" 2>&1 &)

# Small sleep to let product-service bind the port
sleep 1

# Start gateway in background
echo "Starting gateway (logs -> logs/gateway.log)..."
(cd gateway && nohup go run main.go > "$ROOT_DIR/logs/gateway.log" 2>&1 &)

sleep 1

echo "Services started. Check logs in ./logs/ for output."

echo "To stop the services, find their PIDs (e.g., 'ps aux | grep main' or 'pgrep -f "go run main.go"') and kill them."