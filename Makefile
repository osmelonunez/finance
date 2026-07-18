COMPOSE=docker compose -f tools/docker/docker-compose.yaml
COMPOSE_PROD=docker compose -f docker/docker-compose.yaml
COMPOSE_TEST=docker compose -p finance-tests -f tools/docker/docker-compose.test.yaml
IMAGE_REPO?=f1nanc3/finance
VERSION?=3.6.0
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

test-unit:
	@trap '$(COMPOSE_TEST) down -v --remove-orphans' EXIT; \
		$(COMPOSE_TEST) run --rm --build --no-deps tests pytest -m unit

test-routes:
	@trap '$(COMPOSE_TEST) down -v --remove-orphans' EXIT; \
		$(COMPOSE_TEST) run --rm --build tests pytest -m routes

test-release:
	@trap '$(COMPOSE_TEST) down -v --remove-orphans' EXIT; \
		$(COMPOSE_TEST) run --rm --build tests pytest --cov=backend --cov-report=term-missing --cov-fail-under=65

test-clean:
	$(COMPOSE_TEST) down -v --remove-orphans

test-endpoints:
	@trap '$(COMPOSE_TEST) down -v --remove-orphans' EXIT; \
		$(COMPOSE_TEST) run --rm --build --no-deps tests python tests/endpoint_reporting.py
