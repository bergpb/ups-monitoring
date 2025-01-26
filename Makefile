VENV           = .venv
VENV_PYTHON    = $(VENV)/bin/python3
PYTHON         = $(shell which python3)

$(VENV_PYTHON):
	rm -rf $(VENV)
	$(PYTHON) -m venv $(VENV)

venv: $(VENV_PYTHON)

deps-pi: venv
	$(VENV_PYTHON) -m pip install -r requirements-pi.txt

deps-dev: venv
	$(VENV_PYTHON) -m pip install -r requirements-dev.txt

format-check:
	$(VENV_PYTHON) -m black . --check --diff
	$(VENV_PYTHON) -m isort . --check --diff

run:
	$(VENV_PYTHON) ups_hat.py


clean:
	rm ups.sqlite3 ups.log

.PHONY: clean
