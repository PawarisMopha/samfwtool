# SamFWTool Makefile - Easy commands for everything
# Usage: make <command>

.PHONY: install run gui test help clean lint

# Default target
help:
	@echo ""
	@echo "SamFWTool - Easy Commands"
	@echo "========================="
	@echo ""
	@echo "  make install   - Install all dependencies"
	@echo "  make run       - Run CLI (shows help)"
	@echo "  make gui       - Run GUI application"
	@echo "  make test      - Run all tests"
	@echo "  make coverage  - Run tests with coverage report"
	@echo "  make lint      - Run linters (flake8, black check)"
	@echo "  make clean     - Clean temporary files"
	@echo ""
	@echo "CLI Examples:"
	@echo "  make info FILE=firmware.tar.md5    - Show firmware info"
	@echo "  make extract FILE=firmware.tar.md5 - Extract firmware"
	@echo "  make scan FILE=firmware.tar.md5    - Security scan"
	@echo "  make devices                       - List connected devices"
	@echo ""

# Install dependencies
install:
	@echo "Installing SamFWTool..."
	pip install -e . --quiet 2>/dev/null || pip install -e .
	@echo "Done! Run 'make run' to start."

# Run CLI help
run:
	@export PYTHONPATH="$(PWD):$$PYTHONPATH" && python3 -m samfwtool.cli.main --help

# Run GUI
gui:
	@export PYTHONPATH="$(PWD):$$PYTHONPATH" && python3 -m samfwtool.gui.main_gui

# Run tests
test:
	python -m pytest tests/ -v --tb=short

# Run tests with coverage
coverage:
	python -m pytest tests/ -v --tb=short --cov=samfwtool --cov-report=term-missing

# Lint code
lint:
	@echo "Running flake8..."
	@flake8 samfwtool --count --select=E9,F63,F7,F82 --show-source --statistics || true
	@echo "Checking black formatting..."
	@black --check --line-length 100 samfwtool 2>/dev/null || echo "(black not installed or files need formatting)"

# Clean temporary files
clean:
	rm -rf __pycache__ .pytest_cache .coverage coverage.xml
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete 2>/dev/null || true

# CLI Commands with firmware file
info:
	@export PYTHONPATH="$(PWD):$$PYTHONPATH" && python3 -m samfwtool.cli.main info "$(FILE)"

extract:
	@export PYTHONPATH="$(PWD):$$PYTHONPATH" && python3 -m samfwtool.cli.main extract "$(FILE)" -o extracted/

scan:
	@export PYTHONPATH="$(PWD):$$PYTHONPATH" && python3 -m samfwtool.cli.main scan "$(FILE)"

devices:
	@export PYTHONPATH="$(PWD):$$PYTHONPATH" && python3 -m samfwtool.cli.main devices

compare:
	@export PYTHONPATH="$(PWD):$$PYTHONPATH" && python3 -m samfwtool.cli.main compare
