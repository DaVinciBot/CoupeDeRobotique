.PHONY: format lint typecheck docs check all

SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs/source
BUILDDIR      = docs/build

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

docs:
	@echo "▶ Generation de la documentation..."
	$(SPHINXBUILD) -M html "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

all: check docs
