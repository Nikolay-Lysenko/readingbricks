"""
This script makes a notebook with notes that must be selected
according to user query.

@author: Nikolay Lysenko
"""


import os
import json
import argparse
from typing import Set, Tuple
from warnings import warn
from copy import copy

from readingbricks import (
    utils, get_path_to_ipynb_notes, get_path_to_counts_of_tags
)


def parse_cli_args() -> argparse.Namespace:
    """
    Parse arguments passed via Command Line Interface (CLI).

    :return:
        namespace with arguments
    """
    parser = argparse.ArgumentParser(description='Searching for notes')
    parser.add_argument(
        '-e', '--expression', type=str, nargs='+', default='',
        help='logical expression with tags as Boolean variables,'
             'example: (tag1 OR tag2) AND tag3; '
             'notes that match it will be included in a resulting notebook'
    )
    cli_args = parser.parse_args()
    cli_args.expression = ' '.join(cli_args.expression)
    return cli_args


def parse_expression(expression: str) -> Tuple[str, Set[str]]:
    """
    Extract both code template and set of tags from `expression`.

    :param expression:
        logical expression with parentheses and AND and OR operators
    :return:
        template of code that after formatting and evaluation equals
        to value of the `expression` on formatting argument;
        set of tags that appear in the expression
    """
    modified_expression = copy(expression)
    parts_of_syntax = ['(', ')', 'AND', 'OR']
    for reserved_token in parts_of_syntax:
        modified_expression = modified_expression.replace(
            reserved_token, f' {reserved_token} '
        )
    tokens = modified_expression.split()

    parsed_tokens = []
    tags = set()
    before_is_not_a_reserved_token = False
    for token in tokens:
        if token not in parts_of_syntax:
            if before_is_not_a_reserved_token:
                raise ValueError(f'Mistake in expression: {expression}')
            parsed_tokens.append(f"'{token}' in {{0}}")
            tags.add(token)
            before_is_not_a_reserved_token = True
        else:
            parsed_tokens.append(token.lower())
            before_is_not_a_reserved_token = False
    parsed_expression = ' '.join(parsed_tokens)
    return parsed_expression, tags


def validate_and_preprocess_cli_args(
        cli_args: argparse.Namespace
        ) -> argparse.Namespace:
    """
    Inform user about potential mistakes and preprocess input.

    :param cli_args:
        namespace with arguments
    :return:
        namespace with preprocessed arguments
    """
    valid_tags = []
    with open(get_path_to_counts_of_tags(), 'r') as tags_file:
        for line in tags_file:
            valid_tags.append(line.split('\t')[0])
    template, tags = parse_expression(cli_args.expression)
    for tag in tags:
        if tag not in valid_tags:
            warn('There are no notes for {}'.format(tag), RuntimeWarning)
    cli_args.template = template
    return cli_args


def compose_notebook(template: str) -> type(None):
    """
    Create notebook with relevant notes only.

    :param template:
        template of code that after formatting with a list of cell's
        tags returns whether this cell should be selected
    :return:
        None
    """
    path_to_notes = get_path_to_ipynb_notes()
    relevant_cells = []
    for cell in utils.extract_cells(path_to_notes):
        if eval(template.format(str(cell['metadata']['tags']))):
            relevant_cells.append(cell)

    file_names = [
        x for x in os.listdir(path_to_notes)
        if os.path.isfile(os.path.join(path_to_notes, x))
    ]
    arbitrary_file_name = file_names[0]
    with open(os.path.join(path_to_notes, arbitrary_file_name)) as source_file:
        all_content = json.load(source_file)

    content = {k: v for k, v in all_content.items() if k != 'cells'}
    content['cells'] = relevant_cells
    with open('notes_for_the_last_query.ipynb', 'w') as destination_file:
        json.dump(content, destination_file, ensure_ascii=False)


def main():
    cli_args = parse_cli_args()
    cli_args = validate_and_preprocess_cli_args(cli_args)
    compose_notebook(cli_args.template)


if __name__ == '__main__':
    main()
