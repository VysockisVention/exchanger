.PHONY: help install lint format fix test check clean

help:
	@echo "Available commands:"
	@echo "  make install   - install dependencies"
	@echo "  make lint      - run ruff lint"
	@echo "  make format    - run ruff formatter"
	@echo "  make fix       - auto-fix lint issues"
	@echo "  make test      - run tests (NO TEST YET)"
	@echo "  make check     - lint + tests"
	@echo "  make clean     - remove caches"
	@echo "  make dev     	- makes and runs dev"

install:
	poetry install

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

fix:
	poetry run ruff check . --fix
	poetry run ruff format .

test:
	poetry run pytest -vv

check: lint test

dev: check
	poetry run fastapi dev exchanger/main.py

clean:
	rm -rf .pytest_cache .ruff_cache __pycache__
