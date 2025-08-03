#FROM node:18
#
#WORKDIR /app
#
#COPY backend/ .
#COPY .env .
#
## Instala el cliente de PostgreSQL para tener pg_dump disponible
#RUN apt-get update && apt-get install -y postgresql-client
#
#RUN mkdir -p backups
#RUN mkdir -p config
#RUN mkdir -p logs
#
#RUN npm install
#
#CMD ["node", "server.js"]
#
# Imagen base liviana
FROM node:20-alpine

# Actualizar e instalar postgresql-client
RUN apk add --no-cache postgresql-client

# Crear carpeta de trabajo
WORKDIR /app

# Copiar e instalar dependencias
COPY backend/package*.json ./
RUN npm install --omit=dev

# Copiar el resto del código
COPY backend/ ./

# Crear carpetas necesarias
RUN mkdir -p /app/backups /app/config /app/logs

# Establecer variables de entorno
ENV NODE_ENV=production

# Exponer puerto (opcional, útil para debug fuera de HAProxy)
EXPOSE 3001

# Comando para iniciar el servidor
CMD ["npm", "start"]
