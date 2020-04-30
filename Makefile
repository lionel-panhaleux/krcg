.PHONY: validate test init static release update serve deploy clean

# used by CI
validate: static/*.json
	$(foreach f, $^, jsonschema -i $f schemas/$(basename $(notdir $f)).schema.json ;)

test:
	pytest -vvs

init:
	krcg init

static:
	krcg-gen standard amaranth

release: init static validate
	-git commit -m "Update static files" static
	fullrelease

update:
	pip install --upgrade -e .[dev,web]

serve:
	uwsgi --socket 127.0.0.1:8000 --protocol=http  --module src.wsgi:application

clean:
	rm -f src/TWDA.pkl
	rm -f src/VTES.pkl
	rm -rf dist
	rm -rf .pytest_cache
	rm static/*