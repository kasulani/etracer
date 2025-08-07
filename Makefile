.PHONY: help clean install dev-install format lint typecheck test test-coverage all

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
	@echo "  make clean           - Remove build artifacts"
	@echo "  make all             - Run format, lint, typecheck, and test"

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

all: format lint typecheck test