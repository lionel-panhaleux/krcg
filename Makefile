test:
	pytest -vv --pdb --pdbcls=IPython.terminal.debugger:Pdb

release:
	fullrelease

update:
	pip install --upgrade -e .[dev]

serve:
	gunicorn --reload src.flask:app

clean:
	rm src/TWDA.pkl
	rm src/VTES.pkl
	rm -rf dist
	rm -rf .pytest_cache