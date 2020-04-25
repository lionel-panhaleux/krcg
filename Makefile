.PHONY: test static release update serve deploy clean

test:
	pytest -vv --pdb --pdbcls=IPython.terminal.debugger:Pdb

static:
	krcg init
	krcg-gen standard amaranth

release: static
	git commit -m "Update static files" static
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