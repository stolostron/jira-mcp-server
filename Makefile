# Jira MCP Server Makefile

SHELL := /bin/bash

.PHONY: help test tests lint lint-fix install-commands

.DEFAULT_GOAL := help

help:
	@echo "Jira MCP Server - Available targets:"
	@echo ""
	@echo "  test             - Run all tests in the tests/ directory"
	@echo "  tests            - Alias for test"
	@echo "  lint             - Run ruff linter"
	@echo "  lint-fix         - Run ruff linter with auto-fix"
	@echo "  install-commands - Symlink project commands to ~/.claude/commands/"
	@echo "  help             - Show this help message"

test tests:
	python3 -m pytest tests/ -v

lint:
	python3 -m ruff check jira_mcp_server/ tests/

lint-fix:
	python3 -m ruff check --fix jira_mcp_server/ tests/

install-commands:
	@mkdir -p "$(HOME)/.claude/commands"
	@for cmd in "$(CURDIR)"/.claude/commands/*.md; do \
		name="$$(basename "$$cmd")"; \
		ln -sf "$$cmd" "$(HOME)/.claude/commands/$$name"; \
		echo "Symlinked $$name to ~/.claude/commands/"; \
	done
