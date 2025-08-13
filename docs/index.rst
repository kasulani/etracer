.. etracer documentation master file, created by
   sphinx-quickstart on Thu Aug  7 18:43:13 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

eTracer
=====================

A utility package that provides enhanced debugging for Python stack traces with AI-powered error analysis and suggested fixes.

Features
--------

- **Enhanced Stack Traces with color**: Clearer, more readable stack traces with proper formatting and syntax highlighting
- **AI-Powered Analysis**: Uses OpenAI-compatible APIs to analyze errors and provide smart explanations
- **Smart Fix Suggestions**: Get AI-generated suggestions for fixing the issues
- **Multiple Usage Modes**: Decorator, context manager, and global exception handler
- **Local Variable Inspection**: See the values of local variables at the point of error
- **Performance Optimized**: Smart caching to reduce API calls for similar errors

Versioning
---------

This package follows `Semantic Versioning <https://semver.org/>`_ with the following guidelines:

- **0.x.y versions** (e.g., 0.1.0, 0.2.0) indicate **initial development phase**:
    - The API is not yet stable and may change between minor versions
    - Features may be added, modified, or removed without major version changes
    - Not recommended for production-critical systems without pinned versions

- **1.0.0 and above** will indicate a **stable API** with semantic versioning guarantees:
    - MAJOR version for incompatible API changes
    - MINOR version for backwards-compatible functionality additions
    - PATCH version for backwards-compatible bug fixes

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   advanced
   contributing
   deployment
