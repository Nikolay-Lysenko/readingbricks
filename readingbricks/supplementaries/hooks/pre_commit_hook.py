#!/usr/bin/env python
# Be sure that a copy of this file is placed to `../../../.git/hooks`
# directory under name `pre-commit` (without extension).


"""
This script does tasks that are needed for update of both Flask
and Jupyter interfaces of the project. Generally speaking, not all
tasks should be done here, because it is desired to have no
dependencies other than built-in Python packages in Git hooks.
As of now, the list of covered tasks consists of these element:
1) Update a file with counts of tags that appear at least once
   in the most recent editions of notes;
2) Validate human-written notes.
The script is called during every commit automatically if its copy
is placed and named correctly.

@author: Nikolay Lysenko
"""


import os
import subprocess
import json
from collections import Counter
from typing import List, Dict, Generator, Any


def convert_to_absolute_path(relative_path: str) -> str:
    """
    Convert relative path to absolute path.
    """
    script_directory = os.path.dirname(__file__)
    absolute_path = os.path.join(script_directory, relative_path)
    return absolute_path


def extract_cells(path_to_dir: str) -> Generator[Dict[str, Any], None, None]:
    """
    Walk through the specified directory and yield cells of
    Jupyter notebooks from there.
    """
    file_names = [x for x in os.listdir(path_to_dir)
                  if os.path.isfile(path_to_dir + x)]
    for file_name in file_names:
        with open(path_to_dir + file_name) as source_file:
            cells = json.load(source_file)['cells']
            for cell in cells:
                yield cell


def validate_cell(cell: Dict[str, Any]) -> type(None):
    """
    Assert that content of cell is in accordance with assumptions
    lying behind the project.
    """
    content = [line.rstrip('\n') for line in cell['source']]
    msg = f"Cell header must be h2 (i.e. start with ##), found: {content[0]}"
    assert content[0].startswith('## '), msg


def update_list_of_tags(tags: List[str], cell: Dict[str, Any]) -> List[str]:
    """
    Update list of tags occurrences based on a current cell.
    """
    tags.extend(cell['metadata']['tags'])
    return tags


def write_tag_counts(tags: List[str], absolute_path: str) -> type(None):
    """
    Overwrite previous content of the file where statistics are stored.
    Namely, replace old content with data that are based on `tags`.
    """
    counter_of_tags = Counter(tags)
    tags_and_counts = counter_of_tags.most_common()
    sorted_tags_and_counts = sorted(
        tags_and_counts,
        key=lambda tag_and_count: (-tag_and_count[1], tag_and_count[0])
    )
    with open(absolute_path, 'w') as out_file:
        for tag, count in sorted_tags_and_counts:
            out_file.write(f'{tag}\t{count}\n')


def add_to_commit(path_from_git_root: str) -> type(None):
    """
    Add file or directory to the next commit (then post-commit hook
    will commit it and transfer to the current commit before push).
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
    relative_paths = {
        'source': '../../readingbricks/notes/',
        'counts': '../../readingbricks/supplementaries/counts_of_tags.tsv'
    }
    absolute_paths = {
        k: convert_to_absolute_path(v) for k, v in relative_paths.items()
    }
    tags = []
    for cell in extract_cells(absolute_paths['source']):
        validate_cell(cell)
        tags = update_list_of_tags(tags, cell)
    write_tag_counts(tags, absolute_paths['counts'])
    for path in [v.lstrip('../../')
                 for k, v in relative_paths.items() if k != 'source']:
        add_to_commit(path)


if __name__ == '__main__':
    main()
