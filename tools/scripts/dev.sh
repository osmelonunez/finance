#!/bin/bash

WORKSPACE="$HOME/git"
PROJECT_FOLDER="$WORKSPACE/finance/"
PROJECT_DIR="$WORKSPACE/finance/tools/docker-dev/"

# ANSI Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No color

# Function to display menu
function show_menu() {
  echo -e "${CYAN}Select an action:${NC}"
  echo "1) start  - Build and start containers from scratch (no cache)"
  echo "2) update - Rebuild and restart containers (cached build)"
  echo "3) save   - Commit and push changes to Git"
  echo "4) status - Show Git status and running containers"
  echo "5) stop   - Stop and remove all running containers"
  echo "6) wipe   - Stop and remove containers, volumes, images, and build cache"
  echo "7) init   - Clone and build the project (from develop branch)"
  echo "0) exit   - Exit the script"
  echo
  read -p "Enter your choice [0-7]: " choice
}

# Prompt until a valid option is selected
while true; do
  show_menu
  case "$choice" in
    1)
      ACTION="start"
      break
      ;;
    2)
      ACTION="update"
      break
      ;;
    3)
      ACTION="save"
      break
      ;;
    4)
      ACTION="status"
      break
      ;;
    5)
      ACTION="stop"
      break
      ;;
    6)
      ACTION="wipe"
      break
      ;;
    7)
      ACTION="init"
      break
      ;;
    0)
      echo "Goodbye!"
      exit 0
      ;;
    *)
      echo -e "${RED}❌ Invalid choice. Please select a valid option.${NC}"
      ;;
esac
done

# Execute the selected action
case "$ACTION" in
  start)
    echo -e "${BLUE}🔧 Building project...${NC}"
    cd "$PROJECT_DIR" || exit 1
    docker-compose build --no-cache
    docker-compose up -d
    docker ps -a
    echo -e "${CYAN}⏳ Waiting 3 seconds to re-check containers...${NC}"
    sleep 3
    docker ps -a
    echo -e "${GREEN}✅ Project built and deployed successfully.${NC}"
    ;;
  update)
    echo -e "${BLUE}🔄 Updating project...${NC}"
    cd "$PROJECT_DIR" || exit 1
    docker-compose down
    docker-compose build
    docker-compose up -d
    docker ps -a
    echo -e "${CYAN}⏳ Waiting 3 seconds to re-check containers...${NC}"
    sleep 3
    docker ps -a
    echo -e "${GREEN}✅ Project updated and deployed successfully.${NC}"
    ;;
  save)
    echo -e "${BLUE}💾 Saving changes...${NC}"
    cd "$PROJECT_FOLDER" || exit 1
    git add .
    read -p "📝 Enter commit message: " commit_message
    git commit -m "$commit_message"
    git push
    echo -e "${GREEN}✅ Changes committed and pushed successfully.${NC}"
    ;;
  status)
    echo -e "${BLUE}🔎 Checking project status...${NC}"

    if [[ ! -d "$PROJECT_FOLDER" ]]; then
      echo -e "${RED}🚫 Project not found at ${PROJECT_DIR}.${NC}"
      echo -e "${CYAN}👉 Run 'finance init' to clone and deploy it.${NC}"
      exit 1
    fi

    cd "$PROJECT_FOLDER" || exit 1

    if [[ -n $(git status --porcelain) ]]; then
      echo -e "${RED}📌 You have uncommitted changes.${NC}"
      git status --short
    else
      echo -e "${GREEN}✅ No pending changes in Git.${NC}"
    fi

    echo -e "${CYAN}📦 Running containers:${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    count=$(docker ps -q | wc -l | tr -d ' ')
    if [[ "$count" -eq 0 ]]; then
      echo -e "${RED}⚠️  No containers are running.${NC}"
    else
      echo -e "${GREEN}✅ Total: $count container(s) running.${NC}"
    fi
    ;;
  stop)
    echo -e "${RED}⚠️  Stopping and removing containers...${NC}"
    cd "$PROJECT_DIR" || exit 1
    docker-compose down
    echo -e "${GREEN}🗑️  Containers removed.${NC}"
    ;;
  wipe)
    echo -e "${RED}⚠️  Stopping containers and wiping Docker data...${NC}"
    cd "$PROJECT_DIR" || exit 1
    docker-compose down -v
    echo -e "${CYAN}🧹 Removing dangling volumes, images, and build cache...${NC}"
    docker volume prune -f
    docker images -q | grep -v -E "^(c0aab7962b28|815066284948)$" | xargs -r docker rmi -f
    docker builder prune -af
    echo -e "${GREEN}✅ All containers, volumes, images, and cache removed.${NC}"
    ;;
  init)
    echo -e "${BLUE}🔧 Cloning and building the project...${NC}"
    cd "$WORKSPACE" || exit 1
    if [ -d "$PROJECT_FOLDER" ]; then
      echo -e "${RED}⚠️  Project directory already exists: $PROJECT_FOLDER${NC}"
      echo -e "${CYAN}👉 Remove it or rename it if you want to clone a fresh copy.${NC}"
      exit 1
    fi
    git clone -b develop https://github.com/osmelonunez/finance.git || exit 1
    cd "$PROJECT_DIR" || exit 1
    docker-compose build --no-cache
    docker-compose up -d
    docker ps -a
    echo -e "${CYAN}⏳ Waiting 3 seconds to re-check containers...${NC}"
    sleep 3
    docker ps -a
    echo -e "${GREEN}✅ Project cloned, built, and deployed successfully.${NC}"
    ;;
esac