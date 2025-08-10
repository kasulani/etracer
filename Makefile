.PHONY: help clean install dev-install format lint typecheck test test-coverage coverage-report docs docs-html docs-clean docs-open all

PACKAGE_NAME = etracer
PYTHON = python
PIP = pip
PYTEST = pytest

help:
	@echo "Available commands:"
	@echo "  make help            - Show this help message"
	@echo "  make install         - Install the package in editable mode"
	@echo "  make dev-install     - Install the package in development mode with dev dependencies"
	@echo "  make format          - Format code with Black"
	@echo "  make lint            - Run linting with Flake8"
	@echo "  make typecheck       - Run type checking with mypy"
	@echo "  make test            - Run tests with pytest"
	@echo "  make test-coverage   - Run tests with coverage report"
	@echo "  make coverage-report - Open HTML coverage report in browser"
	@echo "  make clean           - Remove build artifacts"
	@echo "  make all             - Run format, lint, typecheck, and test"
	@echo "  make docs            - Build all documentation formats"
	@echo "  make docs-html       - Build HTML documentation"
	@echo "  make docs-clean      - Clean documentation build files"
	@echo "  make docs-open       - Open HTML documentation in browser"

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .mypy_cache
	rm -rf .tox
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

install:
	$(PIP) install -e .

dev-install:
	$(PIP) install -e ".[dev]"

format:
	black src tests

lint:
	flake8 src tests

typecheck:
	mypy src

test:
	$(PYTEST) tests/

test-coverage:
	$(PYTEST) --cov=$(PACKAGE_NAME) --cov-report=term --cov-report=html tests/

docs-clean:
	rm -rf docs/_build

# Install Sphinx and required theme if not already installed
docs-deps:
	$(PIP) install sphinx sphinx-rtd-theme

docs-html: docs-deps
	cd docs && $(MAKE) html

docs: docs-html

# Open the documentation in the default browser
docs-open: docs-html
	open docs/_build/html/index.html

# Open the coverage report in the default browser
coverage-report: test-coverage
	open htmlcov/index.html

all: format lint typecheck test
