PYTHON ?= python3.12

.PHONY: test claims demo check

test:
	$(PYTHON) -m pytest -q

claims:
	$(PYTHON) eval/verify_claims.py

demo:
	$(PYTHON) -m src.btn.ecdl

check: test claims demo
