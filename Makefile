# PENELOPE: Flash-Flood Prediction & Early-Warning Platform
# Tagline: "Data today. Safer tomorrows."
# Pillars: Predict · Prepare · Protect

.PHONY: help dev build up down restart logs test lint train clean seed

help:
	@echo "Available commands:"
	@echo "  make dev       - Run the full stack with Docker Compose"
	@echo "  make build     - Build all Docker containers"
	@echo "  make up        - Start containers in detached mode"
	@echo "  make down      - Stop and remove containers"
	@echo "  make logs      - View logs from all containers"
	@echo "  make test      - Run backend, frontend, and ML tests"
	@echo "  make train     - Train ML models and export MLflow-lite metrics"
	@echo "  make seed      - Ingest real external data and seed villages"
	@echo "  make clean     - Remove cache and temporary artifacts"

dev:
	docker compose up --build

build:
	docker compose build

up:
	docker compose up -d

down:
	docker compose down

restart:
	docker compose restart

logs:
	docker compose logs -f

test:
	pytest apps/api/tests ml/tests -v
	cd apps/web && pnpm test

train:
	python -m ml.train

seed:
	python -m apps.api.seed

lint:
	python -m flake8 apps/api ml --max-line-length=120 --ignore=E203,W503 || true
	cd apps/web && pnpm lint

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

