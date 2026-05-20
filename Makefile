PYTHON ?= python
DATABASE_URL ?= postgresql+psycopg://sociallens:sociallens_dev@localhost:5432/sociallens_bi

.PHONY: setup up down db etl load test lint format demo quality export api-check api frontend-build

setup:
	$(PYTHON) -m venv .venv
	.venv/Scripts/python -m pip install --upgrade pip
	.venv/Scripts/python -m pip install -r requirements-dev.txt

up:
	docker compose up -d

down:
	docker compose down

db:
	docker compose up -d db

etl:
	$(PYTHON) -m etl.cli run --sources facebook,youtube,sample --database-url "$(DATABASE_URL)"

load:
	$(PYTHON) -m etl.cli load --database-url "$(DATABASE_URL)"

quality:
	$(PYTHON) -m etl.cli quality --database-url "$(DATABASE_URL)"

export:
	$(PYTHON) -m etl.cli export --database-url "$(DATABASE_URL)"

test:
	$(PYTHON) -m pytest

api-check:
	$(PYTHON) backend/manage.py check

api:
	$(PYTHON) backend/manage.py runserver 0.0.0.0:8000

frontend-build:
	cd frontend && npm run build

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .

format:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check --fix .

demo: db
	$(PYTHON) -m etl.cli run --sources facebook,youtube,sample --database-url "$(DATABASE_URL)"
	$(PYTHON) -m etl.cli quality --database-url "$(DATABASE_URL)"
	$(PYTHON) -m etl.cli export --database-url "$(DATABASE_URL)"
