# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "etracer"
copyright = "2025, Emmanuel King Kasulani"
author = "Emmanuel King Kasulani"

version = "0.1.0"
release = "0.1.0"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.napoleon",
    "sphinx.ext.autosummary",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

language = "en"

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

# Add src directory to path so Sphinx can find the code
import os
import sys

sys.path.insert(0, os.path.abspath("../src"))

# Configure autodoc
autodoc_typehints = "description"
autodoc_member_order = "bysource"
autoclass_content = "both"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
