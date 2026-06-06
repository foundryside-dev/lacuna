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
	# Trusted local checkout: the repo-owned baseline (deliberate planted
	# specimen flaws) is allowed to clear the gate. CI-on-PR should instead
	# scope to new findings with `--new-since <merge-base>`.
	$(WARDLINE) scan . --fail-on ERROR --trust-suppressions

docs:
	$(PY) -m tour.docs_gen

ci: test scan verify
