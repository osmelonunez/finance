# Finance Project - Docker Setup

This project uses Docker Compose to manage the frontend, backend, database, and proxy services.

## 📦 Services Overview

| Service   | Description                        | Enabled by Default |
|-----------|------------------------------------|---------------------|
| backend   | Node.js API service                | ✅ Yes              |
| frontend  | React/Vite app                     | ✅ Yes              |
| postgres  | PostgreSQL database                | 🔁 Optional (`db`)  |
| haproxy   | Reverse proxy for frontend/backend | 🔁 Optional (`proxy`) |

---

## 🚀 Quick Start

### ▶️ Run App

```bash
sh start.sh
```

---

## ⚙️ Environment Variables

You can configure database connection and other values using the `.env` file.

Example:

```env
DB_HOST=postgres
DB_PORT=5432
DB_NAME=finance
DB_USER=finance
DB_PASSWORD=yourpassword
```

> Make sure `.env` exists in the root of the project when starting containers.

---

## 📌 Notes

- Make sure Docker and Docker Compose are installed.
- Logs can be viewed using:
  ```bash
  docker compose logs -f
  ```

---

## 🧹 Stop and clean everything

```bash
sh stop.sh
```
