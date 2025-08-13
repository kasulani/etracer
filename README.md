# eTracer

[![codecov](https://codecov.io/github/kasulani/etracer/graph/badge.svg?token=J0X12GPW56)](https://codecov.io/github/kasulani/etracer)

A utility package that provides enhanced debugging for Python stack traces with AI-powered error analysis and suggested
fixes.

## Features

- **Enhanced Stack Traces with color**: Clearer, more readable stack traces with proper formatting and syntax
  highlighting
- **AI-Powered Analysis**: Uses OpenAI-compatible APIs to analyze errors and provide smart explanations
- **Smart Fix Suggestions**: Get AI-generated suggestions for fixing the issues
- **Multiple Usage Modes**: Decorator, context manager, and global exception handler
- **Local Variable Inspection**: See the values of local variables at the point of error
- **Performance Optimized**: Smart caching to reduce API calls for similar errors

## Installation

```bash
# Install directly from the repository
pip install git+https://github.com/emmanuelkasulani/etracer.git

# For development, clone the repository and install in editable mode
git clone https://github.com/emmanuelkasulani/etracer.git
cd etracer
pip install -e .
```

## Versioning

This package follows [Semantic Versioning](https://semver.org/) with the following guidelines:

- **0.x.y versions** (e.g., 0.1.0, 0.2.0) indicate **initial development phase**:
    - The API is not yet stable and may change between minor versions
    - Features may be added, modified, or removed without major version changes
    - Not recommended for production-critical systems without pinned versions

- **1.0.0 and above** will indicate a **stable API** with semantic versioning guarantees:
    - MAJOR version for incompatible API changes
    - MINOR version for backwards-compatible functionality additions
    - PATCH version for backwards-compatible bug fixes

The current version is in early development stage, so expect possible API changes until the 1.0.0 release.

## Quick Start

### Basic Usage (No AI)

```python
import etracer

# Enable tracer at the start of your script
etracer.enable()

# Your code here
# Any uncaught exceptions will be processed by tracer
```

In this mode, eTracer will enhance your stack traces with better formatting, with color and local variable inspection,
but it won't
provide AI-powered analysis or suggestions. This is useful for quick debugging without needing an API key or AI
integration.

### With AI-Powered Analysis

```python
import etracer
import os

# Enable tracer with AI
etracer.enable(
    enable_ai=True,
    api_key="your-api-key",
    model="your-preferred-model",
    base_url="https://your-endpoint"
)

# Your code here
# Errors will now get AI-powered explanations and fixes
```

This mode requires specifying an API key, model and base url for an OpenAI-compatible LLM. It will analyze exceptions
using AI and provide detailed explanations and suggested fixes for errors that occur in your code. This is particularly
useful for complex errors where understanding the root cause can be challenging.

You can use local LLMs run on your machine, using Ollama or self-hosted models that support the OpenAI API format.

## Usage Modes

### 1. Global Exception Handler

```python
import etracer

# Enable at the start of your script
etracer.enable(
    enable_ai=True,
    api_key="your-api-key",
    model="your-preferred-model",
    base_url="https://your-endpoint"
)

# All uncaught exceptions will be handled by tracer
```

### 2. Function Decorator

```python
import etracer

# Configure as needed
etracer.enable(
    enable_ai=True,
    api_key="your-api-key",
    model="your-preferred-model",
    base_url="https://your-endpoint"
)


@etracer.analyze
def my_function():
    # If this function raises an exception, tracer will handle it
    x = 1 / 0
```

### 3. Context Manager

```python
import etracer

# Configure as needed
etracer.enable(
    enable_ai=True,
    api_key="your-api-key",
    model="your-preferred-model",
    base_url="https://your-endpoint"
)

# Use context manager for specific code blocks
with etracer.analyzer():
    # Only exceptions in this block will be handled by tracer
    result = "5" + 5  # TypeError
```

### 4. Explicit Analysis

```python
import etracer

# Configure as needed
etracer.enable(
    enable_ai=True,
    api_key="your-api-key",
    model="your-preferred-model",
    base_url="https://your-endpoint"
)

try:
    x = 10
    y = 0
    result = x / y
except Exception as e:
    # Explicitly analyze this exception
    etracer.analyze_exception(e)
```

## Configuration Options

```python
# Basic configuration
etracer.enable(
    enable_ai=True,
    api_key="your-api-key",
    model="your-preferred-model",
    base_url="https://your-endpoint"
)
```

## Example Output

```
================================================================================
 ZeroDivisionError: division by zero
================================================================================
Stack Trace: (most recent call last)
Frame[1/1], file "/Users/emmanuel.kasulani/Projects/etracer/examples.py", line 19, in zero_division
    16:     try:
    17:         x = 10
    18:         y = 0
  > 19:         result = x / y
    20:         print(f"Result: {result}")  # This should not execute

  Local variables:
    x = 10
    y = 0
    e = ZeroDivisionError('division by zero')

Analyzing error with AI...
Finished reading from cache 0.00s
AI Analysis completed in 7.09s
Caching AI response with key 6b466215770b73fc6da24d3601e9ab4e

Analysis:
The error occurs because the code attempts to divide the variable 'x' (which is 10) by 'y' (which is 0). In Python, division by zero is not defined, leading to a ZeroDivisionError. This is a common error when performing arithmetic operations, and it indicates that the denominator in a division operation cannot be zero.
Suggested Fix:
To fix this error, you should check if 'y' is zero before performing the division. You can modify the code as follows:

try:
    x = 10
    y = 0
    if y == 0:
        print("Cannot divide by zero")
    else:
        result = x / y
        print(f"Result: {result}")
except ZeroDivisionError as e:
    print(f"Error: {e}")

This way, you avoid the division by zero and handle the situation gracefully.
================================================================================
End of Traceback
================================================================================
```

## Caching System

Tracer includes a caching system for AI-powered analysis to reduce API costs and improve performance:

- **Cache Location**: A `.tracer_cache` directory in your project's root folder
- **What's Cached**: AI responses for specific error patterns to avoid redundant API calls
- **When Used**: Automatically used when the same error occurs multiple times
- **Manual Cleanup**: Simply delete the `.tracer_cache` directory to clear the cache

```bash
# To manually clear the cache:
rm -rf .tracer_cache
```

This is especially useful during development when you might encounter the same errors repeatedly while fixing issues.

### Future Cache Management

Future versions will include more advanced cache management features such as automatic pruning to keep the cache size
manageable. These features will help maintain optimal performance and disk usage over extended periods of development.

## AI Integration

eTracer uses the OpenAI client library to connect to AI models that support the OpenAI API format. This means it's
compatible with:

- OpenAI models (GPT-3.5, GPT-4, etc.)
- Compatible third-party services that implement the OpenAI API (Anthropic Claude, Cohere, etc.)
- Self-hosted models with OpenAI-compatible APIs (LM Studio, Ollama, etc.)

By default, etracer uses the OpenAI URL `https://api.openai.com/v1` as base URL and `gpt-3.5-turbo` as the default
model. To use a different provider (base URL and model), update the configuration in your code:

```python
# For using Azure OpenAI
etracer.enable(
    enable_ai=True,
    api_key="your-api-key",
    model="your-preferred-model",
    base_url="https://your-endpoint"
)
```

## Requirements

- Python 3.8+
- `pydantic` 2.0+
- `openai` 1.99.6+

## Development

### Setup Development Environment

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/emmanuelkasulani/etracer.git
cd etracer

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Pre-commit Hooks

The project uses pre-commit hooks to ensure code quality before each commit. These hooks automatically run:

- Code formatting with Black
- Import sorting with isort
- Linting with Flake8
- Type checking with MyPy
- Unit tests with pytest
- Various other code quality checks

The hooks will prevent committing if any of these checks fail.

### Code Quality Tools

The project uses several code quality tools that can be run via Make commands:

```bash
# Format code with Black
make format

# Run linting with Flake8
make lint

# Run type checking with MyPy
make typecheck

# Run unit tests with pytest
make test

# Run tests with coverage report
make test-coverage

# Open coverage report in browser
make coverage-report

# Run all quality checks (format, lint, typecheck, test)
make all
```

### Makefile Commands

The following Make commands are available:

| Command                | Description                                       |
|------------------------|---------------------------------------------------|
| `make help`            | Show available commands                           |
| `make install`         | Install the package                               |
| `make dev-install`     | Install in development mode with dev dependencies |
| `make format`          | Format code with Black                            |
| `make lint`            | Run linting with Flake8                           |
| `make typecheck`       | Run type checking with MyPy                       |
| `make test`            | Run unit tests                                    |
| `make test-coverage`   | Run tests with coverage reporting                 |
| `make coverage-report` | Open HTML coverage report in browser              |
| `make clean`           | Remove build artifacts                            |
| `make all`             | Run format, lint, typecheck, and test             |
| `make docs-html`       | Build HTML documentation                          |
| `make docs-open`       | Open HTML documentation in browser                |

## Additional Documentation

For more detailed information about eTracer, refer to the following documents:

- [Contributing Guide](CONTRIBUTING.md) - Guidelines for contributing to the project
- [Deployment Guide](DEPLOYMENT.md) - Information about the release process and versioning
- [Changelog](CHANGELOG.md) - History of changes and updates to the project

## License

Apache License 2.0, see LICENSE for more details.
