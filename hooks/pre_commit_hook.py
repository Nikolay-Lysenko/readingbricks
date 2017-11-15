#!/usr/bin/env python
# Be sure that a copy of this file is placed to `../.git/hooks` directory
# under name `pre-commit` (without extension).


"""
This script updates list of tags that appear at least once in the
most recent version of the master notebook with all notes.
The script is called during every commit automatically if its copy
is placed and named correctly.

@author: Nikolay Lysenko
"""


import os
import subprocess
import json
from typing import List


def convert_to_absolute_path(relative_path: str) -> str:
    """
    Convert relative path to absolute path.
    """
    script_directory = os.path.dirname(__file__)
    absolute_path = os.path.join(script_directory, relative_path)
    return absolute_path


def parse_tags() -> List[str]:
    """
    Parse JSON file with notebooks and extract all unique tags.
    """
    relative_path = '../../notes/all_notes_without_sorting.ipynb'
    absolute_path = convert_to_absolute_path(relative_path)
    cells = json.load(open(absolute_path))['cells']
    tags = set()
    for cell in cells:
        tags.update(set(cell['metadata']['tags']))
    return list(tags)


def write_tags(list_of_tags: List[str]) -> type(None):
    """
    Overwrite previous content of the file with tags from the list.
    """
    relative_path = '../../list_of_tags.txt'
    absolute_path = convert_to_absolute_path(relative_path)
    with open(absolute_path, 'w') as out_file:
        for tag in sorted(list_of_tags):
            out_file.write(tag + '\n')


def add_file_with_tags_to_commit() -> type(None):
    """
    Add file with tags to the next commit (then post-commit hook
    will commit it and transfer to the current commit before push).
    """
    # `git add ..` can not be run from `.git/*`,
    # because this directory is outside of work tree.
    relative_path = '../../'
    absolute_path = convert_to_absolute_path(relative_path)
    path_to_add = 'list_of_tags.txt'
    subprocess.run(
        'git add {}'.format(path_to_add),
        cwd=absolute_path,  # Run above command from top level of the repo.
        shell=True
    )


def main():
    list_of_tags = parse_tags()
    write_tags(list_of_tags)
    add_file_with_tags_to_commit()


if __name__ == '__main__':
    main()
