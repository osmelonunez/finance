COMPOSE=docker compose -f tools/docker/docker-compose.yaml
COMPOSE_PROD=docker compose -f docker/docker-compose.yaml
IMAGE_REPO?=f1nanc3/finance
VERSION?=3.4.1
PLATFORMS?=linux/amd64,linux/arm64

build:
	docker buildx build --platform $(PLATFORMS) -t $(IMAGE_REPO):$(VERSION) -t $(IMAGE_REPO):latest -f tools/docker/Dockerfile --push .

build-local:
	docker build -t $(IMAGE_REPO):latest -f tools/docker/Dockerfile .

up:
	$(COMPOSE) up -d --build

down:
	$(COMPOSE) down

logs:
	$(COMPOSE) logs -f

restart:
	$(COMPOSE) down
	$(COMPOSE) up -d --build

up-prod:
	$(COMPOSE_PROD) up -d

down-prod:
	$(COMPOSE_PROD) down

logs-prod:
	$(COMPOSE_PROD) logs -f

restart-prod:
	$(COMPOSE_PROD) down
	$(COMPOSE_PROD) up -d

audit-deps:
	pip-audit -r backend/requirements.txt
