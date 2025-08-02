#!/bin/bash

set -e

# 🔧 Configuración fija: nombres base de las imágenes
BACKEND_IMAGE="f1nanc3/finance-api"
FRONTEND_IMAGE="f1nanc3/finance-ui"

# 🧾 Solicitar el tag al usuario
read -rp "🔖 Enter the tag to use (e.g., dev, v1.0.0): " IMAGE_TAG

# Validar que no esté vacío
if [ -z "$IMAGE_TAG" ]; then
  echo "❌ No tag provided. Exiting."
  exit 1
fi

# Función reutilizable
tag_and_push() {
  local image_name=$1
  local tag=$2

  local source="${image_name}:${tag}"
  local target="${image_name}:latest"

  echo "📦 Tagging image:"
  echo "   Source: $source"
  echo "   Target: $target"

  if ! docker image inspect "$source" > /dev/null 2>&1; then
    echo "❌ Image '$source' not found locally."
    exit 1
  fi

  docker tag "$source" "$target"
  echo "🚀 Pushing $target..."
  docker push "$target"
  docker push "$source"
}

# 🔁 Aplicar a ambas imágenes
tag_and_push "$BACKEND_IMAGE" "$IMAGE_TAG"
tag_and_push "$FRONTEND_IMAGE" "$IMAGE_TAG"

echo "✅ Both images tagged and pushed as ':latest'."
