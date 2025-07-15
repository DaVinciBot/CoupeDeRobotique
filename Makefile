.PHONY: format lint typecheck check all

format:
	@echo "▶ Formatage avec Ruff, puis Black et isort..."
	ruff format
	black .
	isort .

lint:
	@echo "▶ Linting avec Ruff..."
	-ruff check . --fix

typecheck:
	@echo "▶ Analyse statique avec mypy..."
	-mypy .

check: lint format typecheck

all: check
