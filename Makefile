ifneq (,$(wildcard .env))
include .env
export
endif

PYTHON ?= python
OFFICIAL_YOUTUBE_CHANNEL_IDS ?= UCHEqa2uTf8uXrGWrnU3ThgA,UCq6WR0wWNUuz53c4zeWSa8g,UCqSQSnkQ05fZaCdFMfnLaVw,UCPdzE8o7_ExH7Box2WPSEzw,UCBOjnWu1c_k2v0sEH_2foUg,UCAweoF7181qBWQcz0u8dNhQ,UCK8MrZ48N5EB6umonmj1g-A,UCHCrxNt9H3bDZegTdJznXtw

.PHONY: setup up down db require-database-url require-youtube-api-key etl load test lint format demo demo-local quality export api-check api frontend frontend-build

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

require-database-url:
	$(PYTHON) -c "import os, sys; sys.exit(0 if os.getenv('DATABASE_URL') else 'DATABASE_URL is required. Copy .env.example to .env and set DATABASE_URL')"

require-youtube-api-key:
	$(PYTHON) -c "import os, sys; sys.exit(0 if os.getenv('YOUTUBE_API_KEY') else 'YOUTUBE_API_KEY is required for real YouTube ETL. Set it in .env or use explicit sample/dev commands.')"

etl: require-database-url require-youtube-api-key
	$(PYTHON) -m etl.cli run --sources youtube --channel-ids "$(OFFICIAL_YOUTUBE_CHANNEL_IDS)" --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url "$(DATABASE_URL)"

load: require-database-url
	$(PYTHON) -m etl.cli load --database-url "$(DATABASE_URL)"

quality: require-database-url
	$(PYTHON) -m etl.cli quality --database-url "$(DATABASE_URL)"

export: require-database-url
	$(PYTHON) -m etl.cli export --database-url "$(DATABASE_URL)"

test:
	$(PYTHON) -m pytest

api-check:
	$(PYTHON) backend/manage.py check

api:
	$(PYTHON) backend/manage.py runserver 0.0.0.0:8000

frontend:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

lint:
	$(PYTHON) -m ruff check .
	$(PYTHON) -m black --check .

format:
	$(PYTHON) -m black .
	$(PYTHON) -m ruff check --fix .

demo: require-database-url require-youtube-api-key
	$(PYTHON) -m etl.cli run --sources youtube --channel-ids "$(OFFICIAL_YOUTUBE_CHANNEL_IDS)" --queries= --limit 50 --comments-limit 100 --max-search-pages 12 --database-url "$(DATABASE_URL)"
	$(PYTHON) -m etl.cli quality --database-url "$(DATABASE_URL)"
	$(PYTHON) -m etl.cli export --database-url "$(DATABASE_URL)"

demo-local: db demo
