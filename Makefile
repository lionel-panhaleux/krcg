.PHONY: quality test release update clean

export LOCAL_CARDS = 1

quality:
	black --check krcg tests
	ruff check
	yamllint rulings

test: quality
	pytest -vvs

release:
	fullrelease
	pip install -e ".[dev]"

update:
	pip install --upgrade --upgrade-strategy eager -e ".[dev]"

clean:
	rm -rf dist
	rm -rf .pytest_cache
