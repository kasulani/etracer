# Contributing Guidelines for eTracer

Thank you for considering contributing to eTracer! This document provides guidelines to make the process as smooth as possible for everyone involved.

## Code of Conduct

We expect all contributors to adhere to a high standard of conduct, treating all participants with respect and fostering an inclusive environment.

## Reporting Bugs and Issues

If you find a bug or issue with eTracer, please open an issue in the project's [issue tracker](https://github.com/kasulani/etracer/issues). Please provide as much detail as possible, including:

- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Python version and environment details
- Stack traces or error messages

## Contributing Code

If you would like to contribute code to eTracer, please follow these guidelines:

1. Fork the Project
2. Create your Feature [Branch](#branch-naming-convention-and-commit-message-format) (`git checkout -b major/AmazingFeature`)
3. [Commit](#commit-message-guidelines) your Changes (`git commit -m 'major: Add some AmazingFeature'`)
4. Push to the Branch (`git push origin major/AmazingFeature`)
5. Open a Pull Request

Before submitting a pull request, please ensure that your code adheres to the following guidelines:

- Follow the existing code style and formatting (Black, isort, etc.)
- Write clear and concise [commit messages](#commit-message-guidelines)
- Include tests for any new functionality or bug fixes
- Ensure your changes pass all pre-commit hooks
- Run `make all` to verify all checks pass (formatting, linting, type checking, tests)

By contributing to eTracer, you agree to license your contributions under the terms of the Apache License 2.0.

### Code Review

All code contributions will be reviewed by a maintainer of the project. The maintainer may provide feedback or request changes to the code. Please be patient during the review process.

## Development Environment Setup

To set up the development environment:

```bash
# Clone the repository
git clone https://github.com/kasulani/etracer.git
cd etracer

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

## Quality Assurance

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

# Run all quality checks
make all
```

## Branch Naming Convention and Commit Message Format

The branch naming convention and commit message format are as follows:

- Branch naming convention: `type/branch-name`
- Commit message format: `type: commit message`

The `type` can be one of the following:

- `minor`: Minor changes or a new feature
- `major`: Major changes or breaking change
- `patch`: A bug fix
- `test`: Adding tests
- `chore`: Maintenance tasks such as updating dependencies or configuration files or bootstrap code

### Commit Message Guidelines

To maintain consistency and clarity in our project history, all commit messages should follow the format: `type: commit message`

#### Accepted Types
- **minor**: For minor changes or new features.
- **major**: For major changes or breaking changes.
- **patch**: For bug fixes.
- **test**: For adding or modifying tests.
- **chore**: For maintenance tasks, such as updating dependencies or configuration files or bootstrap code.

#### Examples
- `minor: Add user profile method to Tracer class`
- `major: Refactor cache implementation`
- `patch: Fix null pointer exception in AI analysis handler`
- `test: Add unit tests for cache module`
- `chore: Update CI configuration`

#### Why This Matters
Using a consistent format for commit messages helps:
- Easily identify the purpose and impact of each commit
- Streamline the release process by automatically generating changelogs
- Improve collaboration and understanding among team members

Make sure to follow these guidelines for every commit to keep our project history clean and meaningful!

## Testing

All new features and bug fixes should be accompanied by appropriate tests. Tests are written using pytest and should be placed in the `tests` directory.

To run tests:

```bash
# Run all tests
make test

# Run tests with coverage report
make test-coverage

# Open coverage report in browser
make coverage-report
```

## Documentation

If your changes affect the API or add new features, please update the documentation accordingly. Documentation is built using Sphinx and is located in the `docs` directory.

To build and view the documentation:

```bash
# Build HTML documentation
make docs-html

# Open HTML documentation in browser
make docs-open
```

## License

By contributing to eTracer, you agree to license your contributions under the terms of the Apache License 2.0.

If you have any questions or issues, please open an issue in this repository.
