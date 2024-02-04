.PHONY: quality test release update clean

export GITHUB_BRANCH = V5C-20240201

quality:
	black --check krcg tests
	flake8

test: quality
	pytest -vvs


test-rulings:
	pytest -W error::krcg.rulings.RulingsWarning tests/test_rulings.py

release:
	fullrelease
	pip install -e ".[dev]"

update:
	pip install --upgrade --upgrade-strategy eager -e ".[dev]"

prep:
	python -m cards
	LOCAL_CARDS=1 pytest -vvs

clean:
	rm -rf dist
	rm -rf .pytest_cache
