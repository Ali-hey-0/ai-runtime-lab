# AI Runtime Lab - Automation & Verification Makefile

.PHONY: help test test-phases lint check clean

PYTHON ?= python

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  test         Run all verification tests (pytest and standalone runner)"
	@echo "  test-runner  Run standalone verification runner (zero dependencies)"
	@echo "  lint         Run syntax and bytecode compilation checks"
	@echo "  clean        Remove temporary execution logs and caches"

test: test-runner
	$(PYTHON) -m pytest tests/ -v

test-runner:
	$(PYTHON) test_runner.py

lint:
	$(PYTHON) -m compileall -q .

clean:
	@$(PYTHON) -c "import os, glob; [os.remove(f) for f in glob.glob('**/execution_log.json', recursive=True)]; [os.remove(f) for f in glob.glob('**/state.json', recursive=True)]"
