# Release Process

## Setting up API Tokens

1. Create a TestPyPI account at https://test.pypi.org/account/register/
2. Generate API token at: https://test.pypi.org/manage/account/token/
3. Add the token to your GitHub repository secrets:
   - Go to your repository settings
   - Navigate to Secrets and variables > Actions
   - Add the secret: `TEST_PYPI_API_TOKEN`: Your TestPyPI token

## Testing with TestPyPI

The TestPyPI workflow can be triggered manually:

1. Go to the Actions tab in your repository
2. Select the "Publish to TestPyPI" workflow
3. Click "Run workflow"
4. Enter a version suffix (e.g., `dev0`, `rc1`, etc.)
5. Click "Run workflow"

This will:
1. Check if the PR workflow has passed
2. Build the package with a development version number
3. Publish it to TestPyPI

You can then install your test package using:
```
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ etracer
```

## Official Releases

*Note: The PyPI release workflow will be added in a future PR.*

To create an official release:

1. Update the version in `pyproject.toml`
2. Create and push a new tag matching the version:
   ```
   git tag v0.1.0
   git push origin v0.1.0
   ```
3. Create a new release on GitHub using that tag

## Versioning Strategy

We use [Semantic Versioning](https://semver.org/):
- MAJOR version for incompatible API changes
- MINOR version for backwards-compatible functionality
- PATCH version for backwards-compatible bug fixes
- Pre-release versions use suffixes like `-alpha`, `-beta`, `-rc1`
- Development builds use `.devN` suffix
