#!/bin/bash

set -e

echo "🛑 Finance Project - Stop Services"
echo "----------------------------------"
echo "1. Stop all containers (default)"
echo "2. Stop containers from frontend/backend only setup"
echo "3. Stop and remove volumes (full wipe)"
echo "0. Exit"
echo ""

read -rp "Enter choice [0-3, default: 1]: " CHOICE
CHOICE=${CHOICE:-1}

case "$CHOICE" in
  1)
    echo "🛑 Stopping containers (keeping volumes)..."
    docker compose --profile db --profile proxy down
    ;;
  2)
    echo "🛑 Stopping backend + frontend containers with external network..."
    docker compose -f docker-compose.yml -f docker-compose.override-ext.yml down
    ;;
  3)
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
