# Use bash with strict modes for better error handling
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# Configuration variables
VTESCSV_GITHUB := "https://raw.githubusercontent.com/GiottoVerducci/vtescsv/main"
RULINGS_GITHUB := "https://raw.githubusercontent.com/vtes-biased/vtes-rulings/main/rulings"
VTESCSV_VEKN_NET_FR := "https://www.vekn.net/images/stories/downloads/french/vtescsv_utf8.fr-FR.zip"
VTESCSV_VEKN_NET_ES := "https://www.vekn.net/images/stories/downloads/spanish/vtescsv_utf8.es-ES.zip"

# Default recipe - show available commands
default:
    @just --list

# Run all quality checks and tests
all: quality test

# Run linters and format checks
quality:
    @echo "🔍 Running quality checks..."
    uv run ruff check
    uv run ruff format --check
    uv run mypy krcg
    @echo "✅ Quality checks passed!"

# Run tests (includes quality checks)
test: quality
    @echo "🧪 Running tests..."
    uv run pytest -vvs
    @echo "✅ Tests passed!"

# Sync CSV files from vtescsv repository
sync-cards:
    @echo "📥 Syncing CSV files from vtescsv repository..."
    @mkdir -p krcg/cards
    @curl -f -s -o krcg/cards/vtescrypt.csv "{{ VTESCSV_GITHUB }}/vtescrypt.csv"
    @curl -f -s -o krcg/cards/vteslib.csv "{{ VTESCSV_GITHUB }}/vteslib.csv"
    @curl -f -s -o krcg/cards/vteslibmeta.csv "{{ VTESCSV_GITHUB }}/vteslibmeta.csv"
    @curl -f -s -o krcg/cards/vtessets.csv "{{ VTESCSV_GITHUB }}/vtessets.csv"
    @echo "📥 Syncing rulings YAML files from vtes-biased/vtes-rulings..."
    @curl -f -s -o krcg/cards/groups.yaml "{{ RULINGS_GITHUB }}/groups.yaml"
    @curl -f -s -o krcg/cards/references.yaml "{{ RULINGS_GITHUB }}/references.yaml"
    @curl -f -s -o krcg/cards/rulings.yaml "{{ RULINGS_GITHUB }}/rulings.yaml"
    @echo "📥 Fetching translations from vekn.net..."
    @mkdir -p krcg/cards/vtescsv-fr && curl -f -s "{{ VTESCSV_VEKN_NET_FR }}" | bsdtar -xf - -C krcg/cards/vtescsv-fr
    @mkdir -p krcg/cards/vtescsv-es && curl -f -s "{{ VTESCSV_VEKN_NET_ES }}" | bsdtar -xf - -C krcg/cards/vtescsv-es
    @echo "📥 Fixing CSV files..."
    @python krcg/scripts/fix_csv.py
    @echo "📥 Syncing TWDA..."
    @python krcg/scripts/fetch_twda.py --output krcg/cards/twda.json.xz
    @echo "✅ CSV files synced successfully!"

# Upgrade all dependencies (including dev dependencies)
update: sync-cards
    @echo "📦 Updating dependencies..."
    uv sync --upgrade --dev
    @echo "✅ Dependencies updated!"

# Clean build artifacts
clean-build:
    @echo "🧹 Cleaning build artifacts..."
    rm -rf build dist
    @echo "✅ Cleaned!"

# Clean build and cache artifacts
clean: clean-build
    @echo "🧹 Cleaning cache..."
    rm -rf .pytest_cache .mypy_cache .ruff_cache
    @echo "✅ Cleaned!"

# Ensure we're on main branch and working tree is clean
check:
    @echo "🔍 Checking release prerequisites..."
    @if [[ "$(git branch --show-current)" != "main" ]]; then echo "❌ Not on main branch"; exit 1; fi
    @if [[ -n "$(git status --porcelain)" ]]; then echo "❌ Working directory is dirty"; exit 1; fi
    @echo "✅ Release checks passed!"

# Build the package
build:
    @echo "🔨 Building package..."
    uv build
    @echo "✅ Package built!"

# Bump the version (level: minor | major)
bump level="minor": check
    #!/usr/bin/env bash
    set -euo pipefail
    uv version --bump "{{ level }}"
    VERSION="$(uv version --short)"
    echo "📝 Committing version ${VERSION}..."
    git add pyproject.toml
    git commit -m "Release ${VERSION}" && git tag "v${VERSION}"
    echo "📤 Pushing to remote..."
    git push origin main --tags

# Publish package to PyPI
publish:
    @echo "📦 Publishing to PyPI..."
    @UV_PUBLISH_TOKEN="$(tr -d '\n' < ~/.pypi_token)" uv publish
    @echo "✅ Release completed!"

release: sync-cards clean-build check test
    @just bump minor
    @just build
    @just publish
