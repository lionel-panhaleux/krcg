.PHONY: quality test update clean check release sync-cards

VTESCSV_GITHUB?=https://raw.githubusercontent.com/GiottoVerducci/vtescsv
export VTESCSV_GITHUB_BRANCH=main

quality:
	uv run ruff check
	uv run ruff format --check .

test: quality
	uv run pytest -vvs

update:
	uv sync --upgrade --dev

clean:
	rm -rf dist
	rm -rf .pytest_cache

# check there is no standing change
check:
	@if [[ `git branch --show-current` != "main" ]]; then echo "not on main branch"; exit 1; fi
	@if [[ ! -z `git status --porcelain` ]]; then echo "working directory is dirty"; exit 1; fi

# sync CSV files from vtescsv repository
sync-cards:
	@echo "Syncing CSV files from vtescsv repository..."
	@mkdir -p cards
	@curl -f -s -o cards/vtescrypt.csv $(VTESCSV_GITHUB)/main/vtescrypt.csv
	@curl -f -s -o cards/vteslib.csv $(VTESCSV_GITHUB)/main/vteslib.csv
	@curl -f -s -o cards/vteslibmeta.csv $(VTESCSV_GITHUB)/main/vteslibmeta.csv
	@curl -f -s -o cards/vtessets.csv $(VTESCSV_GITHUB)/main/vtessets.csv
	@echo "✓ CSV files synced successfully!"

release: sync-cards check test
	uv version --bump minor
	$(eval VERSION := $(shell uv version --short))
	git add pyproject.toml
	git commit -m "Release $(VERSION)" && git tag v$(VERSION)
	git push origin main --tags
	uv publish --build
