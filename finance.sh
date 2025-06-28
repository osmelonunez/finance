#!/bin/bash

ACTION="$1"
WORKSPACE="$HOME/git"
PROJECT_DIR="$WORKSPACE/finance"

# Colores ANSI
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No color

# Validar argumento
if [[ -z "$ACTION" || ! "$ACTION" =~ ^(init|update|save|delete)$ ]]; then
  printf "${RED}❌ Comando no válido o no proporcionado.${NC}\n"
  printf "${CYAN}👉 Comandos válidos: $0 {init|update|save|delete}${NC}\n"
  exit 1
fi

case "$ACTION" in
  init)
    printf "${BLUE}🔧 Clonando y compilando proyecto...${NC}\n"
    cd "$WORKSPACE" || exit 1
    git clone -b develop https://github.com/osmelonunez/finance.git || exit 1
    cd "$PROJECT_DIR" || exit 1
    docker-compose build --no-cache
    docker-compose up -d
    docker ps -a
    printf "${CYAN}⏳ Esperando 3 segundos para verificar contenedores nuevamente...${NC}\n"
    sleep 3
    docker ps -a
    printf "${GREEN}✅ Proyecto compilado y desplegado correctamente.${NC}\n"
    ;;
  update)
    printf "${BLUE}🔄 Compilando proyecto...${NC}\n"
    cd "$PROJECT_DIR" || exit 1
    docker-compose down
    #docker-compose build --no-cache
    docker-compose build
    docker-compose up -d
    docker ps -a
    printf "${CYAN}⏳ Esperando 3 segundos para verificar contenedores nuevamente...${NC}\n"
    sleep 3
    docker ps -a
    printf "${GREEN}✅ Proyecto compilado y desplegado correctamente.${NC}\n"
    ;;
  save)
    printf "${BLUE}💾 Guardando cambios...${NC}\n"
    cd "$PROJECT_DIR" || exit 1
    git add .
    git commit -m "save changes"
    git push
    printf "${GREEN}✅ Cambios guardados y enviados a remoto.${NC}\n"
    ;;
  delete)
    printf "${RED}⚠️  Eliminando proyecto y limpiando Docker...${NC}\n"
    cd "$PROJECT_DIR" || exit 1
    docker-compose down
    docker volume rm $(docker volume ls -q | grep -v '^postgres$') > /dev/null 2>&1
    docker rmi -f $(docker images -q | grep -v 1e729d43a0d1) > /dev/null 2>&1
    docker builder prune -a --force
    cd "$WORKSPACE" || exit 1
    rm -rf "$PROJECT_DIR"
    clear
    ls -lh
    printf "${GREEN}🗑️  Proyecto eliminado completamente.${NC}\n"
    ;;
esac

