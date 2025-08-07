Contributing
===========

Contributions to the eTracer project are welcome! Here's how you can contribute:

Setting Up Development Environment
-------------------------------

To set up the development environment:

.. code-block:: bash

    # Clone the repository
    git clone https://github.com/emmanuelkasulani/etracer.git
    cd etracer

    # Install development dependencies
    pip install -e ".[dev]"

Code Quality Tools
---------------

The project uses several code quality tools that can be run via Make commands:

.. code-block:: bash

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

Makefile Commands
--------------

The following Make commands are available:

====================  ===================================================
Command               Description
====================  ===================================================
``make help``         Show available commands
``make install``      Install the package
``make dev-install``  Install in development mode with dev dependencies
``make format``       Format code with Black
``make lint``         Run linting with Flake8
``make typecheck``    Run type checking with MyPy
``make test``         Run unit tests
``make test-coverage`` Run tests with coverage reporting
``make clean``        Remove build artifacts
``make all``          Run format, lint, typecheck, and test
====================  ===================================================

Pull Request Process
-----------------

1. Fork the repository and create a branch from `main`
2. Update the tests if necessary
3. Ensure your code passes all tests and quality checks
4. Submit a pull request

Building the Documentation
-----------------------

To build the documentation:

.. code-block:: bash

    # Install documentation dependencies
    pip install -e ".[docs]"
    
    # Build documentation
    cd docs
    make html
    
    # View documentation
    open _build/html/index.html