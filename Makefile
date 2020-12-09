.PHONY: validate quality test init static release update serve deploy clean sync-images

quality: validate
	black --check krcg tests
	flake8

test: quality
	pytest -vvs

init:
	krcg init


release:
	fullrelease
	pip install -e ".[dev]"

update:
	pip install --upgrade --upgrade-strategy eager -e .[dev,web]

serve:
	source .env && uwsgi --socket 127.0.0.1:8000 --protocol=http  --module krcg.wsgi:application

serve-bot:
	source .env && krcg-bot

clean:
	rm -rf dist
	rm -rf .pytest_cache
