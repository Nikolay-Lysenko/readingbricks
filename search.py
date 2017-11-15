"""
This script makes a notebook with notes that must be selected
according to user query.

@author: Nikolay Lysenko
"""


import os
import json
import argparse
from typing import Set
from warnings import warn


def parse_cli_args() -> argparse.Namespace:
    """
    Parse arguments passed via Command Line Interface (CLI).

    :return:
        namespace with arguments
    """
    parser = argparse.ArgumentParser(description='Searching for notes')
    parser.add_argument(
        '-t', '--tags', type=str, nargs='+', default='',
        help='tags such that notes marked with at least one of them '
             'will be included'
    )
    cli_args = parser.parse_args()
    return cli_args


def validate_and_preprocess_cli_args(
        cli_args: argparse.Namespace
        ) -> argparse.Namespace:
    """
    Inform user about potential mistakes and preprocess input.

    :param cli_args:
        namespace with arguments
    :return:
        namespace with validated arguments
    """
    cli_args.tags = set(cli_args.tags)
    valid_tags = []
    with open('list_of_tags.txt') as tags_file:
        for line in tags_file:
            valid_tags.append(line.rstrip('\n'))
    for tag in cli_args.tags:
        if tag not in valid_tags:
            warn('There are no notes for {}'.format(tag), RuntimeWarning)
    return cli_args


def compose_notebook(set_of_tags: Set[str]) -> type(None):
    """
    Create notebook with relevant notes only.

    :param set_of_tags:
        tags of cells that must be included
    :return:
        None
    """
    relative_path = 'notes/all_notes_without_sorting.ipynb'
    script_directory = os.path.dirname(__file__)
    absolute_path = os.path.join(script_directory, relative_path)
    all_content = json.load(open(absolute_path))
    all_cells = all_content['cells']
    relevant_cells = []
    for cell in all_cells:
        if set(cell['metadata']['tags']) & set_of_tags:
            relevant_cells.append(cell)
    content = {k: v for k, v in all_content.items() if k != 'cells'}
    content['cells'] = relevant_cells
    json.dump(
        content,
        open('notes/notes_for_the_last_query.ipynb', 'w'),
        ensure_ascii=False
    )


def main():
    cli_args = parse_cli_args()
    cli_args = validate_and_preprocess_cli_args(cli_args)
    compose_notebook(cli_args.tags)


if __name__ == '__main__':
    main()
