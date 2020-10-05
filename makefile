
.PHONY: venvcheck
venvcheck:
ifeq ("$(VIRTUAL_ENV)","")
	@echo "Venv is not activated!"
	@echo "Activate venv first."
	@echo
	exit 1
endif

install: venvcheck
	@poetry install

test: venvcheck
	@tox

lint: venvcheck
	@black --line-length 88 --exclude '.venv|.tox'  .

example: venvcheck
	@python -m example
