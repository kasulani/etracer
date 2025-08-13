Deployment Process
==================

PyPI Release Process
-------------------

The project uses semantic versioning and automated PyPI releases through GitHub Actions.

How It Works
^^^^^^^^^^^

1. The version is automatically updated based on the branch prefix when a PR is merged:

   - **MAJOR** version: Use ``major/`` branch prefix (e.g., ``major/redesign-api``)
   - **MINOR** version: Use ``feature/`` branch prefix (e.g., ``feature/add-new-method``)
   - **PATCH** version: Use ``bugfix/`` or ``hotfix/`` branch prefix (e.g., ``bugfix/fix-null-pointer``)
   - No version change: Other prefixes like ``docs/``, ``chore/``, etc.

2. When a PR is merged, the automated workflow:

   - Determines the next version based on the branch prefix
   - Updates version in ``pyproject.toml``
   - Commits the version change
   - Creates a new tag
   - Runs tests to ensure quality
   - Builds the package
   - Publishes to PyPI
   - Creates a GitHub release with the new version

Requirements
^^^^^^^^^^^

- A PyPI API token must be stored in GitHub repository secrets as ``PYPI_API_TOKEN``
- The workflow runs on Python 3.13

Manual Release
^^^^^^^^^^^^^

Automated versioning is the primary method, but if needed, you can manually trigger a release:

1. Create a PR from a branch with the appropriate prefix:

   - ``major/`` for major version increment
   - ``feature/`` for minor version increment
   - ``bugfix/`` or ``hotfix/`` for patch version increment

2. Get the PR approved and merged
3. The automated workflow will handle the rest

For test releases to TestPyPI, use the separate ``testpypi.yml`` workflow via manual trigger.
