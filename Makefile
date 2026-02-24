# Jira MCP Server Makefile

SHELL := /bin/bash

.PHONY: help tests

.DEFAULT_GOAL := help

help:
	@echo "Jira MCP Server - Available targets:"
	@echo ""
	@echo "  tests - Run all tests in the tests/ directory"
	@echo "  help  - Show this help message"

tests:
	python3 -m pytest tests/ -v
