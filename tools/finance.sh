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
if [[ -z "$ACTION" || ! "$ACTION" =~ ^(init|update|save|delete|status)$ ]]; then
  printf "${RED}❌ Comando no válido o no proporcionado.${NC}\n"
  printf "${CYAN}👉 Comandos válidos: $0 {init|update|save|delete|status}${NC}\n"
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
    before=$(docker system df -v | grep "Total space used" | awk '{print $4,$5}')
    printf "${RED}⚠️  Eliminando proyecto y limpiando Docker...${NC}\n"
    cd "$PROJECT_DIR" || exit 1
    docker-compose down
    docker volume rm $(docker volume ls -q | grep -v '^finance_postgres$') > /dev/null 2>&1
    docker rmi -f $(docker images -q | grep -v 1e729d43a0d1 | grep -v 815066284948) > /dev/null 2>&1
    docker builder prune -a --force
    cd "$WORKSPACE" || exit 1
    rm -rf "$PROJECT_DIR"
    after=$(docker system df -v | grep "Total space used" | awk '{print $4,$5}')
    clear
    printf "${CYAN}💡 Espacio usado antes: $before${NC}\n"
    printf "${CYAN}💡 Espacio usado después: $after${NC}\n"
    printf "${GREEN}🗑️  Proyecto eliminado completamente.${NC}\n"
    ;;
  status)
    printf "${BLUE}🔎 Verificando estado del proyecto...${NC}\n"

    if [[ ! -d "$PROJECT_DIR" ]]; then
      printf "${RED}🚫 El proyecto no está desplegado en ${PROJECT_DIR}.${NC}\n"
      printf "${CYAN}👉 Ejecuta 'finance init' para clonarlo y desplegarlo.${NC}\n"
      exit 1
    fi

    cd "$PROJECT_DIR" || exit 1

    # Verificar cambios pendientes
    if [[ -n $(git status --porcelain) ]]; then
      printf "${RED}📌 Tienes cambios sin subir.${NC}\n"
      git status --short
    else
      printf "${GREEN}✅ No hay cambios pendientes en Git.${NC}\n"
    fi

    # Verificar contenedores activos
    printf "${CYAN}📦 Contenedores en ejecución:${NC}\n"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

    count=$(docker ps -q | wc -l | tr -d ' ')
    if [[ "$count" -eq 0 ]]; then
      printf "${RED}⚠️  No hay contenedores corriendo.${NC}\n"
    else
      printf "${GREEN}✅ Total: $count contenedor(es) activo(s).${NC}\n"
    fi
    ;;
esac

