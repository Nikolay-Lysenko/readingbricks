#!/usr/bin/env python
# Be sure that a copy of this file is placed to `../../../.git/hooks`
# directory under name `pre-commit` (without extension).


"""
This script automates update-related tasks.

Generally speaking, not all tasks should be done here, because
it is desired to have no dependencies other than built-in Python packages
in Git hooks.
As of now, the list of covered tasks consists of these element:
1) Update a file with counts of tags that appear at least once
   in the most recent editions of notes;
2) Validate human-written notes.
The script is called during every commit automatically if its copy
is placed and named correctly.

Author: Nikolay Lysenko
"""


import os
import subprocess
import sys
from collections import Counter
from typing import List, Dict, Any


def convert_to_absolute_path(relative_path: str) -> str:
    """Convert relative path to absolute path."""
    script_directory = os.path.dirname(__file__)
    absolute_path = os.path.join(script_directory, relative_path)
    return absolute_path


def validate_cell_header(
        headers: List[str], cell: Dict[str, Any]
) -> List[str]:
    """Check that header of a cell meets project specifications."""
    content = [line.rstrip('\n') for line in cell['source']]
    curr_header = content[0]

    msg = f"Cell header must be h2 (i.e. start with ##), found: {curr_header}"
    if not curr_header.startswith('## '):
        raise ValueError(msg)

    msg = f"Each header must appear only once, '{curr_header}' is duplicated"
    if curr_header in headers:
        raise ValueError(msg)

    headers.append(curr_header)
    return headers


def validate_tag(tag: str) -> None:
    """Check that a tag can be a name of SQLite table."""
    if not tag:
        raise ValueError("Empty tags are not allowed")
    if '-' in tag:
        raise ValueError("Symbol '-' is prohibited in a tag name")
    if tag[0].isdigit():
        raise ValueError("Tags must not start with digit")


def update_list_of_tags(tags: List[str], cell: Dict[str, Any]) -> List[str]:
    """Update list of tags occurrences based on a current cell."""
    current_tags = cell['metadata']['tags']
    for tag in current_tags:
        validate_tag(tag)
    tags.extend(current_tags)
    return tags


def write_tag_counts(tags: List[str], absolute_path: str) -> None:
    """Overwrite previous content of the file with tag statistics."""
    counter_of_tags = Counter(tags)
    tags_and_counts = counter_of_tags.most_common()
    sorted_tags_and_counts = sorted(
        tags_and_counts,
        key=lambda tag_and_count: (-tag_and_count[1], tag_and_count[0])
    )
    with open(absolute_path, 'w') as out_file:
        for tag, count in sorted_tags_and_counts:
            out_file.write(f'{tag}\t{count}\n')


def add_to_commit(path_from_git_root: str) -> None:
    """
    Add file or directory to the next commit.

    Then post-commit hook will commit it and transfer
    to the current commit before push.
    """
    # `git add ..` can not be run from `.git/*`,
    # because this directory is outside of work tree.
    cwd_relative_path = '../../'
    cwd_absolute_path = convert_to_absolute_path(cwd_relative_path)
    subprocess.run(
        'git add {}'.format(path_from_git_root),
        cwd=cwd_absolute_path,  # Run above command from top level of the repo.
        shell=True
    )


def main():
    """Manage updates."""
    relative_paths = {
        'source': '../../notes/',
        'counts': '../../supplementaries/counts_of_tags.tsv'
    }
    absolute_paths = {
        k: convert_to_absolute_path(v) for k, v in relative_paths.items()
    }

    sys.path.append(
        convert_to_absolute_path('../../readingbricks/')
    )
    import utils

    headers = []
    tags = []
    for cell in utils.extract_cells(absolute_paths['source']):
        headers = validate_cell_header(headers, cell)
        tags = update_list_of_tags(tags, cell)
    write_tag_counts(tags, absolute_paths['counts'])
    for path in [v.lstrip('../../')
                 for k, v in relative_paths.items() if k != 'source']:
        add_to_commit(path)


if __name__ == '__main__':
    main()
