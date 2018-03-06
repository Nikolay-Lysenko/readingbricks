"""
This script provides tools for turning Jupyter notebook cells with
notes in Markdown into separate Markdown files used by Flask app.

@author: Nikolay Lysenko
"""


import os
from typing import List, Dict, Any

from readingbricks.ipynb_utils import extract_cells


class MarkdownDirectoryCreator:
    """
    Instances of this class can parse notes in Jupyter format, convert
    notes content to Markdown, and store each note in a separate file
    within a specified directory. Also instances of the class can
    remove files that correspond to removed or renamed notes.

    :param path_to_ipynb_notes:
        path to directory where Jupyter files with notes are located
    :param path_to_markdown_notes:
        path to directory where Markdown files created based on
        Jupyter files should be located
    """

    def __init__(self, path_to_ipynb_notes: str, path_to_markdown_notes: str):
        self.__path_to_ipynb_notes = path_to_ipynb_notes
        self.__path_to_markdown_notes = path_to_markdown_notes

    def __provide_empty_directory(self) -> type(None):
        # Make directory for Markdown files if it does not exist
        # and delete all files from there if it is not empty.
        if not os.path.isdir(self.__path_to_markdown_notes):
            os.mkdir(self.__path_to_markdown_notes)
        for file_name in os.listdir(self.__path_to_markdown_notes):
            file_name = os.path.join(self.__path_to_markdown_notes, file_name)
            if os.path.isfile(file_name):
                os.unlink(file_name)

    @staticmethod
    def __insert_blank_line_before_each_list(content: List[str]) -> List[str]:
        # Insert blank line before each Markdown list when it is needed
        # for Misaka parser.
        list_markers = ['* ', '- ', '+ ', '1. ']
        result = []
        for first, second in zip(content, content[1:]):
            result.append(first)
            if any([second.startswith(x) for x in list_markers]) and first:
                result.append('')
        result.append(content[-1])
        return result

    def __copy_cell_content_to_markdown_file(
            self,
            cell: Dict[str, Any],
            ) -> type(None):
        # Extract content of cell and save it as Markdown file in the
        # specified directory.
        content = [line.rstrip('\n') for line in cell['source']]
        content = self.__insert_blank_line_before_each_list(content)
        file_name = content[0].lstrip('## ')
        file_path = (
            os.path.join(self.__path_to_markdown_notes, file_name) + '.md'
        )
        with open(file_path, 'w') as destination_file:
            for line in content:
                destination_file.write(line + '\n')

    def create_or_update_directory_with_markdown_notes(self) -> type(None):
        """
        Delete previous editions of notes in Markdown if there are any
        and create the ones based on the current state of files from
        directory with notes.

        :return:
            None
        """
        self.__provide_empty_directory()
        for cell in extract_cells(self.__path_to_ipynb_notes):
            self.__copy_cell_content_to_markdown_file(cell)
