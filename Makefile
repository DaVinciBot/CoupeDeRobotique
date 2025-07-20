.PHONY: format lint typecheck check all

format:
	@echo "▶ Formatage avec Ruff, puis Black et isort..."
	isort .
	ruff format
	black .

lint:
	@echo "▶ Linting avec Ruff..."
	-ruff check . --fix > ruff-baseline.txt
	@echo "▶ Linting avec pydoclint..."
	pydoclint .

typecheck:
	@echo "▶ Analyse statique avec mypy..."
	-mypy .

check: lint format typecheck

all: check
