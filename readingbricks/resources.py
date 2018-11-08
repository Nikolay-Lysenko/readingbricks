"""
This script provides tools for creating and updating resources.

Here, a resource is anything that has below properties:
1) it is used by the Flask application;
2) it should not be added to Git repository.

For example, a resource can be SQLite database or a Markdown
file with content that is very close to that of a Jupyter note.

Author: Nikolay Lysenko
"""


import sqlite3
import os
from collections import defaultdict
from typing import List, Dict, Any, Optional
from contextlib import closing

from readingbricks import utils, settings


class DatabaseCreator:
    """
    Creator of SQLite database mapping a tag to a list of notes.

    Namely, tables from the database represent tags and rows of a table
    represent notes tagged with the corresponding tag.

    :param path_to_ipynb_notes:
        path to directory where Jupyter files with notes are located
    :param path_to_db:
        path to SQLite database; if this file already exists, it will
        be overwritten, else the file will be created
    """

    def __init__(self, path_to_ipynb_notes: str, path_to_db: str):
        """Initialize an instance."""
        self.__path_to_ipynb_notes = path_to_ipynb_notes
        self.__path_to_db = path_to_db

    @staticmethod
    def __update_mapping_of_tags_to_notes(
            tag_to_notes: defaultdict,
            cell: Dict[str, Any]
    ) -> defaultdict:
        # Store cell header in lists that relates to its tags.
        cell_header = cell['source'][0].rstrip('\n')
        cell_header = cell_header.lstrip('## ')
        cell_tags = cell['metadata']['tags'] + ['all_notes']
        for tag in cell_tags:
            tag_to_notes[tag].append(cell_header)
        return tag_to_notes

    def __write_tag_to_notes_mapping_to_db(
            self,
            tag_to_notes: defaultdict
    ) -> None:
        # Write content of `tag_to_notes` to the target DB.
        with closing(sqlite3.connect(self.__path_to_db)) as conn:
            with utils.open_transaction(conn) as cur:
                for k, v in tag_to_notes.items():
                    cur.execute(
                        f"CREATE TABLE IF NOT EXISTS {k} (note_id VARCHAR)"
                    )
                    cur.execute(
                        f"""
                        CREATE UNIQUE INDEX IF NOT EXISTS
                            {k}_index
                        ON
                            {k} (note_id)
                        """
                    )
                    cur.execute(
                        f"DELETE FROM {k}"
                    )
                    for note_title in v:
                        cur.execute(
                            f"INSERT INTO {k} (note_id) VALUES (?)",
                            (utils.compress(note_title),)
                        )
            with closing(conn.cursor()) as cur:
                cur.execute('VACUUM')

    def create_or_update_db(self) -> None:
        """
        Create SQLite database if it does not exist or update it else.

        :return:
            None
        """
        tag_to_notes = defaultdict(lambda: [])
        for cell in utils.extract_cells(self.__path_to_ipynb_notes):
            tag_to_notes = self.__update_mapping_of_tags_to_notes(
                tag_to_notes, cell
            )
        self.__write_tag_to_notes_mapping_to_db(tag_to_notes)


class MarkdownDirectoryCreator:
    """
    Converter of notes in Jupyter format to Markdown.

    Each note is stored in a separate file within
    a specified directory.
    Also instances of the class can remove files that correspond to
    removed or renamed notes.

    :param path_to_ipynb_notes:
        path to directory where Jupyter files with notes are located
    :param path_to_markdown_notes:
        path to directory where Markdown files created based on
        Jupyter files should be located
    """

    def __init__(self, path_to_ipynb_notes: str, path_to_markdown_notes: str):
        """Initialize an instance."""
        self.__path_to_ipynb_notes = path_to_ipynb_notes
        self.__path_to_markdown_notes = path_to_markdown_notes

    def __provide_empty_directory(self) -> None:  # pragma: no cover
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
    ) -> None:
        # Extract content of cell and save it as Markdown file in the
        # specified directory.
        content = [line.rstrip('\n') for line in cell['source']]
        content = self.__insert_blank_line_before_each_list(content)
        note_title = content[0].lstrip('## ')
        file_name = utils.compress(note_title)
        file_path = (
            os.path.join(self.__path_to_markdown_notes, file_name) + '.md'
        )
        with open(file_path, 'w') as destination_file:
            for line in content:
                destination_file.write(line + '\n')

    def create_or_update_directory_with_markdown_notes(self) -> None:
        """
        Manage directory with Markdown notes.

        Delete previous editions of notes in Markdown if there are any
        and create the ones based on the current editions of files from
        directory with notes.

        :return:
            None
        """
        self.__provide_empty_directory()
        for cell in utils.extract_cells(self.__path_to_ipynb_notes):
            self.__copy_cell_content_to_markdown_file(cell)


def provide_resources(
        ipynb_path: Optional[str] = None,
        markdown_path: Optional[str] = None,
        db_path: Optional[str] = None
) -> None:
    """
    Create or update all resources.

    :return:
        None
    """
    ipynb_path = ipynb_path or settings.get_path_to_ipynb_notes()
    markdown_path = markdown_path or settings.get_path_to_markdown_notes()
    db_path = db_path or settings.get_path_to_db()

    md_creator = MarkdownDirectoryCreator(ipynb_path, markdown_path)
    md_creator.create_or_update_directory_with_markdown_notes()
    db_creator = DatabaseCreator(ipynb_path, db_path)
    db_creator.create_or_update_db()


if __name__ == '__main__':
    provide_resources()
