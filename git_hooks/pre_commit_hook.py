#!/usr/bin/env python
# Be sure that a copy of this file is placed to `../.git/hooks` directory
# under the name `pre-commit` (without extension).


"""
Automate pre-commit validation.

As of now, this script runs the below tasks:
1) Check code style with 'lint' section of `tox.ini`;
2) Validate note headers and tags;
3) Validate internal links.

Not all tasks can be run from here, because it is desired to have no dependencies
other than built-in Python packages in Git hooks.

Author: Nikolay Lysenko
"""


import os
import re
import subprocess
import sys
from typing import Any


# NB: If note name contains parentheses, all after the first closing parenthesis is lost.
INTERNAL_URL_PATTERN = "\\[.+\\]\\(([^h][^\\)]*)\\)"
INTERNAL_URL_REGEXP = re.compile(INTERNAL_URL_PATTERN)


def convert_to_absolute_path(relative_path: str) -> str:
    """Convert relative path to absolute path."""
    script_directory = os.path.dirname(__file__)
    absolute_path = os.path.abspath(os.path.join(script_directory, relative_path))
    return absolute_path


def lint() -> None:
    """Analyze code statically."""
    rel_path_to_repo_root = '../../'  # It is assumed that script is located at `.git/hooks`.
    abs_path_to_repo_root = convert_to_absolute_path(rel_path_to_repo_root)
    result = subprocess.run('tox -e lint', cwd=abs_path_to_repo_root, shell=True)
    return_code = result.returncode
    if return_code:
        raise ValueError('Lint target failed.')


def validate_cell_header(header: str, previous_headers: list[str]) -> None:
    """Check that header of a cell meets project specifications."""
    if not header.startswith('## '):
        raise ValueError(f"Cell header must be h2 (i.e., it must start with ##), found: {header}")
    if header in previous_headers:
        raise ValueError(f"Each header must appear only once, '{header}' is duplicated")


def update_list_of_headers(headers: list[str], cell: dict[str, Any]) -> list[str]:
    """Add cell header to list of headers if it is valid."""
    content = [line.rstrip('\n') for line in cell['source']]
    header = content[0]
    validate_cell_header(header, headers)
    headers.append(header)
    return headers


def validate_tag(tag: str) -> None:
    """Check that a tag can be a name of SQLite table."""
    if not tag:
        raise ValueError("Empty tags are not allowed")
    if '-' in tag:
        raise ValueError("Symbol '-' is prohibited in a tag name")
    if tag[0].isdigit():
        raise ValueError("Tags must not start with digit")


def update_list_of_tags(tags: list[str], cell: dict[str, Any]) -> list[str]:
    """Update list of tags occurrences based on a current cell."""
    current_tags = cell['metadata']['tags']
    for tag in current_tags:
        validate_tag(tag)
    tags.extend(current_tags)
    return tags


def update_list_of_internal_urls(internal_urls: list[str], cell: dict[str, Any]) -> list[str]:
    """Update list of URLs pointing to other pages of the app."""
    for line in cell['source']:
        internal_urls.extend(INTERNAL_URL_REGEXP.findall(line))
    return internal_urls


def validate_internal_urls(internal_urls: list[str], headers: list[str], tags: list[str]) -> None:
    """Validate URLs pointing to other pages of the app."""
    # See comment about `INTERNAL_URL_PATTERN` - this is why `rstrip(')')` is applied.
    headers = [x.lstrip('# ').rstrip(')') for x in headers]
    for internal_url in internal_urls:
        split_url = internal_url.split('/')
        if split_url[0] == '__root_url__':
            conditions = [
                split_url[2] == 'notes' and split_url[3] in headers,
                split_url[2] == 'tags' and split_url[3] in tags
            ]
        elif split_url[0] == '__home_url__':
            conditions = [
                split_url[1] == 'notes' and split_url[2] in headers,
                split_url[1] == 'tags' and split_url[2] in tags
            ]
        else:
            raise ValueError(
                "URLs must start with 'http', '__root_url__', or '__home_url__', "
                f"but '{internal_url}' found"
            )
        if not any(conditions):
            raise ValueError(f"URL '{internal_url}' points to non-existent page")


def main():
    """Validate commit."""
    lint()

    relative_path_to_notes = '../../notes/'
    absolute_path_to_notes = convert_to_absolute_path(relative_path_to_notes)

    sys.path.append(convert_to_absolute_path('../../readingbricks/'))
    import utils

    for directory_name in os.listdir(absolute_path_to_notes):
        directory_path = os.path.join(absolute_path_to_notes, directory_name)
        if not os.path.isdir(directory_path):
            continue
        headers = []
        tags = []
        internal_urls = []
        for cell in utils.extract_cells(directory_path):
            headers = update_list_of_headers(headers, cell)
            tags = update_list_of_tags(tags, cell)
            internal_urls = update_list_of_internal_urls(internal_urls, cell)
        validate_internal_urls(internal_urls, headers, tags)


if __name__ == '__main__':
    main()
