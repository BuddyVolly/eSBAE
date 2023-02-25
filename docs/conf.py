"""Configuration file for the Sphinx documentation builder.

This file only contains a selection of the most common options. For a full
list see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Path setup ----------------------------------------------------------------

from datetime import datetime

# from e_sbae import __author__, __version__

# -- Project information -------------------------------------------------------

project = "eSBAE"
author = "FAO"
copyright = f"2023-{datetime.now().year}, FAO"
release = "0.0.0"

# -- General configuration -----------------------------------------------------

extensions = ["sphinx_design"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

# -- Options for HTML output ---------------------------------------------------

html_theme = "pydata_sphinx_theme"
html_context = {
    "github_user": "BuddyVolly",
    "github_repo": "eSBAE",
    "github_version": "main",
    "doc_path": "docs",
}
html_theme_options = {
    "logo": {"text": project},
    "use_edit_page_button": True,
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/BuddyVolly/eSBAE",
            "icon": "fa-brands fa-github",
        }
    ],
}
