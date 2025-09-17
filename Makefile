.PHONY: format lint check docs auto all

format:
	@echo "▶ Formatage avec isort et Ruff..."
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
	-pdoc --output-dir docs -t docs/pdoc_templates common/arena common/geometry common/gpio common/led_strip common/navigation common/strategy common/teensy common/usb_com/python common/utils common/video
# 	robot1/rasp/boombot_strategy robot1/rasp/brains robot1/rasp/controllers robot1/rasp/sensors

auto:
	make all
	make auto

all: check docs


# TODO: workspace copy toml and make
