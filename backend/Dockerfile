FROM node:18

WORKDIR /app

COPY backend/ .
COPY .env .

# Instala el cliente de PostgreSQL para tener pg_dump disponible
RUN apt-get update && apt-get install -y postgresql-client

RUN mkdir -p backups
RUN mkdir -p config
RUN mkdir -p logs

RUN npm install

CMD ["node", "server.js"]
