.PHONY: format lint check auto all

format:
	@echo "▶ Formatage avec Ruff, puis Black et isort..."
	isort .
	ruff format

lint:
	@echo "▶ Linting avec Ruff..."
	-ruff check . --fix > ruff-baseline.txt
	@echo "▶ Linting avec pydoclint..."
	pydoclint .
	@echo "▶ Linting avec pylint..."
	-pylint --output=pylint-baseline.txt .
	@echo "▶ Linting avec pyright..."
	-pyright --level warning --outputjson > pyright-baseline.json

check: format lint

auto:
	make all
	make auto

all: check
