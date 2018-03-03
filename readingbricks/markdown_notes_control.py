"""
This script parses notes in Jupyter format, converts their content
to Markdown, and stores each note in a separate file within a
directory that is managed by this script. Also this script can
remove files that correspond to removed or renamed notes.

@author: Nikolay Lysenko
"""


import os
from typing import List, Dict, Any

from readingbricks.ipynb_utils import extract_cells
from readingbricks.path_configuration import (
    get_path_to_ipynb_notes, get_path_to_markdown_notes
)


def provide_empty_directory(absolute_dir_name: str) -> type(None):
    """
    Make directory if it does not exist and delete all files
    from there if it is not empty.
    """
    if not os.path.isdir(absolute_dir_name):
        os.mkdir(absolute_dir_name)
    for file_name in os.listdir(absolute_dir_name):
        file_name = os.path.join(absolute_dir_name, file_name)
        if os.path.isfile(file_name):
            os.unlink(file_name)


def insert_blank_line_before_each_list(content: List[str]) -> List[str]:
    """
    Insert blank line before each Markdown list when it is needed
    for Misaka parser.
    """
    list_markers = ['* ', '- ', '+ ', '1. ']
    result = []
    for first, second in zip(content, content[1:]):
        result.append(first)
        if any([second.startswith(x) for x in list_markers]) and first:
            result.append('')
    result.append(content[-1])
    return result


def copy_cell_content_to_markdown_file(
        cell: Dict[str, Any], destination_dir_path: str
        ) -> type(None):
    """
    Extract content of cell and save it as Markdown file in the
    specified directory.
    """
    content = [line.rstrip('\n') for line in cell['source']]
    content = insert_blank_line_before_each_list(content)
    destination_name = content[0].lstrip('## ')
    destination_path = (
        os.path.join(destination_dir_path, destination_name) + '.md'
    )
    with open(destination_path, 'w') as destination_file:
        for line in content:
            destination_file.write(line + '\n')


def refresh_directory_with_markdown_notes() -> type(None):
    """
    Delete previous editions of notes in Markdown and replace them
    with the ones based on the current state of files from master
    directory with notes.
    """
    absolute_paths = {
        'source': get_path_to_ipynb_notes(),
        'destination': get_path_to_markdown_notes()
    }
    provide_empty_directory(absolute_paths['destination'])
    for cell in extract_cells(absolute_paths['source']):
        copy_cell_content_to_markdown_file(cell, absolute_paths['destination'])


if __name__ == '__main__':
    refresh_directory_with_markdown_notes()
