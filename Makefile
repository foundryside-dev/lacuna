PY := .venv/bin/python
WARDLINE := /home/john/.local/bin/wardline

.PHONY: tour verify test scan docs ci

tour:
	$(PY) -m tour tour
	$(PY) -m tour.docs_gen

verify:
	$(PY) -m tour verify

test:
	$(PY) -m pytest

scan:
	$(WARDLINE) scan . --fail-on ERROR

docs:
	$(PY) -m tour.docs_gen

ci: test scan verify
