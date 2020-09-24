.PHONY: validate quality test init static release update serve deploy clean sync-images

LACKEY_FOLDER ?= /Applications/LackeyCCG
REMOTE ?= krcg.org:projects/images.krcg.org/dist

# used by CI
validate: static/*.json
	$(foreach f, $^, jsonschema -i $f schemas/$(basename $(notdir $f)).schema.json ;)

quality: validate
	black --check krcg tests
	flake8

test: quality
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
	source .env && uwsgi --socket 127.0.0.1:8000 --protocol=http  --module krcg.wsgi:application

serve-bot:
	source .env && krcg-bot

clean:
	rm -f `python -c "import tempfile as t; print(t.gettempdir())"`/krcg-vtes.pkl
	rm -f `python -c "import tempfile as t; print(t.gettempdir())"`/krcg-twda.pkl
	rm -rf dist
	rm -rf .pytest_cache

sync-images:
	# Official card name was changed, but it is not reprinted yet - let's keep both for now
	cp ${LACKEY_FOLDER}/plugins/vtes/sets/setimages/general/regomotus.jpg ${LACKEY_FOLDER}/plugins/vtes/sets/setimages/general/regomotum.jpg
	rsync -rptov --delete-after -e ssh ${LACKEY_FOLDER}/plugins/vtes/sets/setimages/general/ ${REMOTE}
