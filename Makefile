# Makefile

VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

# Полный запуск dev-среды
dev: venv db-up dev-server

# Production сборка и запуск
prod:
	docker compose up -d

venv:
	python3 -m venv $(VENV)
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

db-up:
	docker compose up -d db

dev-server:
	$(VENV)/bin/uvicorn src.main:app --reload

down:
	docker compose down
