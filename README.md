# 💰 Finance – Personal Finance Application

![GitHub release (latest by date)](https://img.shields.io/github/v/release/osmelonunez/finance)
![License](https://img.shields.io/github/license/osmelonunez/finance)
![Repo size](https://img.shields.io/github/repo-size/osmelonunez/finance)

📊 Finance is a personal and household finance management web application. It consists of two components:
- `finance-ui`: A modern frontend built with Vite and Node.js 20
- `finance-api`: A secure REST API built with Node.js 20

🔗 GitHub Repository: [osmelonunez/finance](https://github.com/osmelonunez/finance)

---

## 🚀 Features

- Track income, expenses, and manage savings.
- Visualize financial summaries
- RESTful API with authentication and budget management
- Built with modern and scalable Node.js architecture

---

## ⚙️ How to download and work with this project

This project is prepared for both development and production environments using Docker.

---

### 🧪 Development environment setup

1. Clone the repository:

```bash
git clone https://github.com/osmelonunez/finance.git
cd finance
```

2. Configure environment variables:

Edit the file `tools/docker-dev/.env` and define at least the following:

```env
UI_TAG=X.X.X
API_TAG=X.X.X
```

You may modify other variables if needed.

3. Start the development environment:

```bash
tools/scripts/dev.sh
```

This script will launch the services using `tools/docker-dev/docker-compose.yml`.

4. Publish a stable image to Docker Hub:

Use the following script, passing the version tag you want to publish:

```bash
tools/scripts/tag-and-push.sh X.X.X
```

Replace `X.X.X` with the version tag for your image.

---


### 🚀 Run in production

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

You will be prompted with options:

1. Full stack (Backend + Frontend + PostgreSQL + HAProxy)
2. Backend + Frontend only (uses external network `public`)
3. Backend + Frontend + PostgreSQL
4. Backend + Frontend + HAProxy

> If you choose option 2, make sure the external Docker network `public` exists:

```bash
docker network create public
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

You will be prompted with options:

1. Stop all containers (profiles: `db`, `proxy`)
2. Stop containers from frontend/backend only setup (uses override)
3. Stop and remove volumes (delete all data)

---

## 🐳 Docker Images

Docker Hub repositories:

- [f1nanc3/finance-ui](https://hub.docker.com/r/f1nanc3/finance-ui)
- [f1nanc3/finance-api](https://hub.docker.com/r/f1nanc3/finance-api)

---

## 📄 License

This project is licensed under the [GNU General Public License v3.0 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.html).

See the [LICENSE](./LICENSE) file for full license text and conditions.