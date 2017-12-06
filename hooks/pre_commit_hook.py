#!/usr/bin/env python
# Be sure that a copy of this file is placed to `../.git/hooks` directory
# under name `pre-commit` (without extension).


"""
This script updates a file with counts of tags that appear
at least once in the most recent version of the master notebook
with all notes.
The script is called during every commit automatically if its copy
is placed and named correctly.

@author: Nikolay Lysenko
"""


import os
import subprocess
import json
from collections import Counter


def convert_to_absolute_path(relative_path: str) -> str:
    """
    Convert relative path to absolute path.
    """
    script_directory = os.path.dirname(__file__)
    absolute_path = os.path.join(script_directory, relative_path)
    return absolute_path


def count_tags() -> Counter:
    """
    Parse JSON file of the master notebook and extract frequencies
    of tags.
    """
    relative_path = '../../notes/all_notes_without_sorting.ipynb'
    absolute_path = convert_to_absolute_path(relative_path)
    cells = json.load(open(absolute_path))['cells']
    tags = []
    for cell in cells:
        tags.extend(cell['metadata']['tags'])
    return Counter(tags)


def write_tag_counts(counter_of_tags: Counter) -> type(None):
    """
    Overwrite previous content of the file containing statistics,
    replace old content with data that are based on `counter_of_tags`.
    """
    relative_path = '../../counts_of_tags.tsv'
    absolute_path = convert_to_absolute_path(relative_path)
    tags_and_counts = counter_of_tags.most_common()
    sorted_tags_and_counts = sorted(
        tags_and_counts,
        key=lambda tag_and_count: (-tag_and_count[1], tag_and_count[0])
    )
    with open(absolute_path, 'w') as out_file:
        for tag, count in sorted_tags_and_counts:
            out_file.write(f'{tag}\t{count}\n')


def add_file_with_counts_to_commit() -> type(None):
    """
    Add file with tag statistics to the next commit (then
    post-commit hook will commit it and transfer to the
    current commit before push).
    """
    # `git add ..` can not be run from `.git/*`,
    # because this directory is outside of work tree.
    relative_path = '../../'
    absolute_path = convert_to_absolute_path(relative_path)
    path_to_add = 'counts_of_tags.tsv'
    subprocess.run(
        'git add {}'.format(path_to_add),
        cwd=absolute_path,  # Run above command from top level of the repo.
        shell=True
    )


def main():
    counter_of_tags = count_tags()
    write_tag_counts(counter_of_tags)
    add_file_with_counts_to_commit()


if __name__ == '__main__':
    main()
