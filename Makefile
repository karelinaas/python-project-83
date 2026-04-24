PORT ?= 8000

lint:
	uv run ruff check page_analyzer

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
