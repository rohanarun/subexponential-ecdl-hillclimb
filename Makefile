PYTHON ?= python3.12

.PHONY: test claims results demo check

test:
	$(PYTHON) -m pytest -q

claims:
	$(PYTHON) eval/verify_claims.py

results:
	$(PYTHON) eval/verify_results.py

demo:
	$(PYTHON) -m src.btn.ecdl

check: test claims results demo
