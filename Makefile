# Jira MCP Server Makefile

SHELL := /bin/bash

# Prefer repo .venv when present (avoids broken global fastmcp installs).
PYTHON := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

.PHONY: help test tests lint format format-check install-commands verify-startup bootstrap

.DEFAULT_GOAL := help

help:
	@echo "Jira MCP Server - Available targets:"
	@echo ""
	@echo "  bootstrap        - Create .venv and install package + dev deps"
	@echo "  verify-startup   - Smoke-test fastmcp + server imports"
	@echo "  test             - Run all tests in the tests/ directory"
	@echo "  tests            - Alias for test"
	@echo "  lint             - Run pytest, black, and isort checks"
	@echo "  format           - Auto-format with black and isort"
	@echo "  format-check     - Check black and isort without writing"
	@echo "  install-commands - Symlink project commands to ~/.claude/commands/"
	@echo "  help             - Show this help message"
	@echo ""
	@echo "Python: $(PYTHON)"

bootstrap:
	python3.12 -m venv .venv
	.venv/bin/pip install -U pip
	.venv/bin/pip install -e '.[dev]'
	@echo "Bootstrap done. Use: $(CURDIR)/.venv/bin/python"

verify-startup:
	bash scripts/verify-startup.sh

test tests:
	$(PYTHON) -m pytest tests/ -v

lint: format-check test

format:
	$(PYTHON) -m black jira_mcp_server tests
	$(PYTHON) -m isort jira_mcp_server tests

format-check:
	$(PYTHON) -m black --check jira_mcp_server tests
	$(PYTHON) -m isort --check-only jira_mcp_server tests

install-commands:
	@mkdir -p "$(HOME)/.claude/commands"
	@for cmd in "$(CURDIR)"/.claude/commands/*.md; do \
		name="$$(basename "$$cmd")"; \
		ln -sf "$$cmd" "$(HOME)/.claude/commands/$$name"; \
		echo "Symlinked $$name to ~/.claude/commands/"; \
	done
