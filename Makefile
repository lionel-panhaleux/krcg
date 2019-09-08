test:
	pytest -vv --pdb --pdbcls=IPython.terminal.debugger:Pdb

release:
	fullrelease

update:
	pip install --upgrade -e .[dev]
