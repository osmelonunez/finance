#!/bin/bash

set -e

echo "🛑 Finance Project - Stop Services"
echo "----------------------------------"
echo "1. Stop all containers"
echo "2. Stop all containers and remove volumes (delete data)"
echo "0. Exit"
echo ""

read -rp "Enter choice [0-2]: " CHOICE

case "$CHOICE" in
  1)
    echo "🛑 Stopping containers (keeping volumes)..."
    docker compose --profile db --profile proxy down
    ;;
  2)
    echo "🔥 Stopping containers and removing volumes (data will be lost)..."
    docker compose --profile db --profile proxy down -v
    ;;
  0)
    echo "👋 Exiting."
    exit 0
    ;;
  *)
    echo "❌ Invalid option."
    exit 1
    ;;
esac
