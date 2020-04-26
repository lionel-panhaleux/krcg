.PHONY: validate test init static release update serve deploy clean

# used by CI
validate: static/*.json
	$(foreach f, $^, jsonschema -i $f schemas/$(basename $(notdir $f)).schema.json ;)

test:
	pytest -vv --pdb --pdbcls=IPython.terminal.debugger:Pdb

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
	gunicorn --reload --access-logfile - src.flask:app

deploy:
	git push --force heroku master

clean:
	rm src/TWDA.pkl
	rm src/VTES.pkl
	rm -rf dist
	rm -rf .pytest_cache