"""
This is the script that initializes Flask app.

Author: Nikolay Lysenko
"""


import os

from flask import Flask


# Closures for paths to sources are provided below.
# All path dispatching must be done here in order to have a single
# place that is affected by changes in project structure.

def get_path_to_ipynb_notes() -> str:
    """
    Get absolute path to directory with Jupyter notebooks containing
    human-written notes.
    """
    path = os.path.join(os.path.dirname(__file__), '..', 'notes')
    return path


def get_path_to_markdown_notes() -> str:
    """
    Get absolute path to directory with automatically created
    Markdown files with notes.
    """
    path = os.path.join(os.path.dirname(__file__), '.markdown_notes')
    return path


def get_path_to_db() -> str:
    """
    Get absolute path to SQLite DB that is used by the Flask app.
    """
    path = os.path.join(os.path.dirname(__file__), 'tag_to_notes.db')
    return path


def get_path_to_counts_of_tags() -> str:
    """
    Get absolute path to a TSV file with counts of tags.
    """
    path = os.path.join(
        os.path.dirname(__file__),
        '..', 'supplementaries', 'counts_of_tags.tsv'
    )
    return path


app = Flask(__name__)
app.config['path_to_ipynb_notes'] = get_path_to_ipynb_notes()
app.config['path_to_markdown_notes'] = get_path_to_markdown_notes()
app.config['path_to_db'] = get_path_to_db()
app.config['path_to_counts_of_tags'] = get_path_to_counts_of_tags()


# Flask requires to import `views` after `app` is set
# in order to decorate views and register routes.
# Thus, E402 and F401 style violations should be ignored here.
import readingbricks.views  # noqa: E402, F401
