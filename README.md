# eTracer

A utility package that provides enhanced debugging for Python stack traces with AI-powered error analysis and suggested
fixes.

## Features

- **Enhanced Stack Traces with color**: Clearer, more readable stack traces with proper formatting and syntax
  highlighting
- **AI-Powered Analysis**: Uses OpenAI's API to analyze errors and provide smart explanations
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

## Quick Start

### Basic Usage (No AI)

```python
import etracer

# Enable tracer at the start of your script
etracer.enable()

# Your code here
# Any uncaught exceptions will be processed by tracer
```

### With AI-Powered Analysis

```python
import etracer
import os

# Configure AI (using environment variable for API key)
API_KEY = os.environ.get("OPENAI_API_KEY")
etracer.configure_ai(api_key=API_KEY, model="gpt-3.5-turbo")

# Enable tracer with AI
etracer.enable(ai_enabled=True)

# Your code here
# Errors will now get AI-powered explanations and fixes
```

## Usage Modes

### 1. Global Exception Handler

```python
import etracer

# Enable at the start of your script
etracer.enable(verbosity=2, show_locals=True, ai_enabled=True)

# All uncaught exceptions will be handled by tracer
```

### 2. Function Decorator

```python
import etracer

# Configure as needed
etracer.enable()


@etracer.debug
def my_function():
    # If this function raises an exception, tracer will handle it
    x = 1 / 0
```

### 3. Context Manager

```python
import etracer

# Configure as needed
etracer.enable()

# Use context manager for specific code blocks
with etracer.catch_errors():
    # Only exceptions in this block will be handled by tracer
    result = "5" + 5  # TypeError
```

### 4. Explicit Analysis

```python
import etracer

# Configure as needed
etracer.enable()

try:
    # Your code that might raise an exception
    result = my_list[10]
except Exception as e:
    # Explicitly analyze this exception
    etracer.analyze_exception(e)
```

## Configuration Options

```python
# Full configuration with defaults
etracer.enable(
    verbosity=2,  # 0=minimal, 1=normal, 2=detailed
    show_locals=True,  # Whether to show local variables
    ai_enabled=False,  # Whether to use AI for analysis
    use_cache=False  # Use smart caching for AI responses
)

# Configure AI integration
etracer.configure_ai(
    api_key="your-api-key",  # Required for AI analysis
    model="gpt-3.5-turbo",  # AI model to use
    enabled=True,  # Enable AI analysis
    use_cache=True  # Cache API responses
)
```

## Example Output

```
========================================================================
ZeroDivisionError: division by zero
========================================================================

Stack Trace: (most recent call last)

[1/1] File "example.py", line 10, in test_function
line 8:     x = 10
line 9:     y = 0
  > 10:     result = x / y
line 11:     return result
line 12: 

Local variables:
    x = 10
    y = 0

Analysis:
You attempted to divide by zero, which is a mathematical error. In this case, 
the variable 'y' has a value of 0, and you're trying to divide 'x' (which is 10) 
by 'y'. Division by zero is not allowed in mathematics or programming.

Suggested Fix:
Add a check to prevent division by zero:

if y != 0:
    result = x / y
else:
    result = 0  # or some other fallback value, or raise a custom exception
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

## Requirements

- Python 3.8+
- `pydantic` 2.0+
- `openai` 1.0+
- OpenAI API key (for AI-powered analysis)

## Development

### Setup Development Environment

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/emmanuelkasulani/etracer.git
cd etracer

# Install development dependencies
pip install -e ".[dev]"
```

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

# Run all quality checks (format, lint, typecheck, test)
make all
```

### Makefile Commands

The following Make commands are available:

| Command | Description |
|---------|-------------|
| `make help` | Show available commands |
| `make install` | Install the package |
| `make dev-install` | Install in development mode with dev dependencies |
| `make format` | Format code with Black |
| `make lint` | Run linting with Flake8 |
| `make typecheck` | Run type checking with MyPy |
| `make test` | Run unit tests |
| `make test-coverage` | Run tests with coverage reporting |
| `make clean` | Remove build artifacts |
| `make all` | Run format, lint, typecheck, and test |

## License
Apache License 2.0, see LICENSE for more details.
