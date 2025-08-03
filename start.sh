#!/bin/bash

set -e

echo "🚀 Finance Project - Docker Launcher"
echo "-----------------------------------"
echo "Choose what you want to launch:"
echo "1. Full stack (Backend + Frontend + PostgreSQL + HAProxy) [default]"
echo "2. Backend + Frontend only"
echo "3. Backend + Frontend + PostgreSQL"
echo "4. Backend + Frontend + HAProxy"
echo "0. Exit"
echo ""

read -rp "Enter choice [0-4, default: 1]: " CHOICE
CHOICE=${CHOICE:-1}

case "$CHOICE" in
  1)
    echo "▶️ Starting full stack..."
    docker compose --profile db --profile proxy up -d
    ;;
  2)
    echo "▶️ Starting backend + frontend with external network 'public'..."
    docker compose -f docker-compose.yml -f docker-compose.override-ext.yml up -d
    ;;
  3)
    echo "▶️ Starting backend + frontend + postgres..."
    docker compose --profile db up -d
    ;;
  4)
    echo "▶️ Starting backend + frontend + haproxy..."
    docker compose --profile proxy up -d
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
