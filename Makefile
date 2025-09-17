.PHONY: format lint check docs auto all

format:
	@echo "▶ Formatage avec isort et Ruff..."
	isort --sl .
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

docs:
	@echo "▶ Génération de la documentation avec pdoc..."
	find docs/* -mindepth 0 -maxdepth 0 ! -name pdoc_templates -exec rm -rf {} +
	pdoc -o docs -d google -t docs/pdoc_templates common rasp

auto:
	make all
	make auto

all: check docs


# TODO: workspace copy toml and make
