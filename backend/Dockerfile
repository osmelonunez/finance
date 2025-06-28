FROM node:18
WORKDIR /app

COPY backend/ .
COPY .env .

RUN npm install

CMD ["node", "server.js"]
