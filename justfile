# Use bash with strict modes for better error handling
set shell := ["bash", "-eu", "-o", "pipefail", "-c"]

# Configuration variables
export VTESCSV_GITHUB := "https://raw.githubusercontent.com/GiottoVerducci/vtescsv"
export VTESCSV_GITHUB_BRANCH := "main"

# Default recipe - show available commands
default:
    @just --list

# Run all quality checks and tests
all: quality test

# Run linters and format checks
quality:
    #!/usr/bin/env bash
    echo "🔍 Running quality checks..."
    uv run ruff check
    uv run ruff format --check .
    echo "✅ Quality checks passed!"

# Run tests (includes quality checks)
test: quality
    #!/usr/bin/env bash
    echo "🧪 Running tests..."
    uv run pytest -vvs
    uv run mypy krcg
    echo "✅ Tests passed!"

# Upgrade all dependencies (including dev dependencies)
update:
    #!/usr/bin/env bash
    echo "📦 Updating dependencies..."
    uv sync --upgrade --dev
    echo "✅ Dependencies updated!"

# Clean build and cache artifacts
clean:
    #!/usr/bin/env bash
    echo "🧹 Cleaning build artifacts..."
    rm -rf build dist .pytest_cache .mypy_cache .ruff_cache
    echo "✅ Cleaned!"

# Ensure we're on master branch and working tree is clean
check:
    #!/usr/bin/env bash
    echo "🔍 Checking release prerequisites..."
    if [[ "$(git branch --show-current)" != "master" ]]; then 
        echo "❌ Not on master branch"; 
        exit 1; 
    fi
    if [[ -n "$(git status --porcelain)" ]]; then 
        echo "❌ Working directory is dirty"; 
        exit 1; 
    fi
    echo "✅ Release checks passed!"

# Sync CSV files from vtescsv repository
sync-cards:
    #!/usr/bin/env bash
    echo "📥 Syncing CSV files from vtescsv repository..."
    mkdir -p cards
    curl -f -s -o cards/vtescrypt.csv {{VTESCSV_GITHUB}}/{{VTESCSV_GITHUB_BRANCH}}/vtescrypt.csv
    curl -f -s -o cards/vteslib.csv {{VTESCSV_GITHUB}}/{{VTESCSV_GITHUB_BRANCH}}/vteslib.csv
    curl -f -s -o cards/vteslibmeta.csv {{VTESCSV_GITHUB}}/{{VTESCSV_GITHUB_BRANCH}}/vteslibmeta.csv
    curl -f -s -o cards/vtessets.csv {{VTESCSV_GITHUB}}/{{VTESCSV_GITHUB_BRANCH}}/vtessets.csv
    echo "✅ CSV files synced successfully!"

# Build the package
build:
    #!/usr/bin/env bash
    echo "🔨 Building package..."
    uv build
    echo "✅ Package built!"

# Release flow: sync data, check state, test, bump version, tag, push, publish
release: sync-cards check test
    #!/usr/bin/env bash
    echo "🚀 Starting release process..."
    uv version --bump minor
    VERSION="$(uv version --short)"
    echo "📝 Committing version ${VERSION}..."
    git add pyproject.toml
    git commit -m "Release ${VERSION}" && git tag "v${VERSION}"
    echo "📤 Pushing to remote..."
    git push origin master --tags
    echo "📦 Publishing to PyPI..."
    uv publish --build
    echo "✅ Release ${VERSION} completed!"
