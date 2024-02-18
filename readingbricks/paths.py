"""
Manage paths to resources.

Author: Nikolay Lysenko
"""


import os


def get_path_to_ipynb_notes() -> str:
    """
    Get absolute path to directory containing notes in .ipynb format for all domains.

    :return:
        path to top-level directory with notes
    """
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'notes'))
    return path


def get_path_to_markdown_notes(domain: str) -> str:
    """
    Get absolute path to directory with Markdown files with notes.

    :param domain:
        name of domain (like 'machine_learning' or 'computer_science')
    :return:
        path to directory with notes in Markdown
    """
    path = os.path.join(os.path.dirname(__file__), 'resources', domain, 'markdown_notes')
    return path


def get_path_to_tag_counts(domain: str) -> str:
    """
    Get absolute path to a TSV file with counts of tags.

    :param domain:
        name of domain (like 'machine_learning' or 'computer_science')
    :return:
        path to the file with tag counts
    """
    path = os.path.join(os.path.dirname(__file__), 'resources', domain, 'counts_of_tags.tsv')
    return path


def get_path_to_tag_to_notes_db(domain: str) -> str:
    """
    Get absolute path to SQLite DB that maps tags to corresponding notes.

    :param domain:
        name of domain (like 'machine_learning' or 'computer_science')
    :return:
        path to the database that maps tags to notes
    """
    path = os.path.join(os.path.dirname(__file__), 'resources', domain, 'tag_to_notes.db')
    return path
