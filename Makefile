PORT ?= 8000

lint:
	uv run ruff check page_analyzer

lint-fix:
	uv run ruff check page_analyzer --fix

install:
	uv sync

dev:
	uv run flask --debug --app page_analyzer:app run

start:
	uv run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

build:
	./build.sh

render-start:
	gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

stop:
	@lsof -t -i :$(PORT) | xargs kill -9 || true

restart: stop start

test:
	uv run pytest

test-cov:
	uv run pytest --cov=page_analyzer --cov-report=term-missing --cov-report=html

test-clean:
	rm -rf htmlcov/
	rm -f .coverage
