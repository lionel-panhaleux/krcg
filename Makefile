.PHONY: quality test release update clean

export VTESCSV_GITHUB_BRANCH=main

quality:
	black --check krcg tests
	ruff check

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
