# Jira MCP Server Makefile

SHELL := /bin/bash

.PHONY: help test tests lint format format-check install-commands

.DEFAULT_GOAL := help

help:
	@echo "Jira MCP Server - Available targets:"
	@echo ""
	@echo "  test             - Run all tests in the tests/ directory"
	@echo "  tests            - Alias for test"
	@echo "  lint             - Run pytest, black, and isort checks"
	@echo "  format           - Auto-format with black and isort"
	@echo "  format-check     - Check black and isort without writing"
	@echo "  install-commands - Symlink project commands to ~/.claude/commands/"
	@echo "  help             - Show this help message"

test tests:
	python3 -m pytest tests/ -v

lint: format-check test

format:
	python3 -m black jira_mcp_server tests
	python3 -m isort jira_mcp_server tests

format-check:
	python3 -m black --check jira_mcp_server tests
	python3 -m isort --check-only jira_mcp_server tests

install-commands:
	@mkdir -p "$(HOME)/.claude/commands"
	@for cmd in "$(CURDIR)"/.claude/commands/*.md; do \
		name="$$(basename "$$cmd")"; \
		ln -sf "$$cmd" "$(HOME)/.claude/commands/$$name"; \
		echo "Symlinked $$name to ~/.claude/commands/"; \
	done
