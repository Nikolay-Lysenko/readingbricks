"""
This script makes a notebook with snippets that are tagged
according to user query.

@author: Nikolay Lysenko
"""


import os
import json
import argparse
from typing import Set


def compose_notebook(set_of_tags: Set[str]) -> type(None):
    """
    Create notebook with relevant snippets only.

    :param set_of_tags:
        tags of cells that must be included
    :return:
        None
    """
    relative_path = 'snippets/all_snippets_without_sorting.ipynb'
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
        open('snippets/snippets_that_match_query.ipynb', 'w'),
        ensure_ascii=False
    )


def parse_cli_args() -> argparse.Namespace:
    """
    Parse arguments passed via Command Line Interface (CLI).

    :return:
        namespace with arguments
    """
    parser = argparse.ArgumentParser(description='Searching for snippets')
    parser.add_argument(
        '-t', '--tags', type=str, nargs='+', default='',
        help='tags such that snippets marked with at least one of them '
             'will be included'
    )
    cli_args = parser.parse_args()
    return cli_args


def main():
    cli_args = parse_cli_args()
    compose_notebook(set(cli_args.tags))


if __name__ == '__main__':
    main()
