"""
Make resources.

Here, a resource is anything that has below properties:
1) it is used by the Flask application;
2) it should not be added to Git repository.

Author: Nikolay Lysenko
"""


import os
import sqlite3
from collections import defaultdict
from contextlib import closing
from typing import Any

from readingbricks.constants import (
    NOTES_DIR,
    RESOURCES_DIR,
    MARKDOWN_DIR_NAME,
    TAG_COUNTS_FILE_NAME,
    TAG_TO_NOTES_DB_FILE_NAME,
)
from readingbricks.utils import compress, extract_cells, open_transaction


class MarkdownNotesMaker:
    """
    Converter of Jupyter cells with notes to Markdown files.

    Each note is stored in a separate file within a specified directory.
    Also instances of the class can remove files that correspond to removed or renamed notes.

    :param path_to_markdown_notes:
        path to directory where Markdown files are going to be saved
    """

    def __init__(self, path_to_markdown_notes: str):
        """Initialize an instance."""
        self.__path_to_markdown_notes = path_to_markdown_notes

    def provide_empty_directory(self) -> None:  # pragma: no cover
        """
        Ensure that directory for Markdown files exists and is empty.

        :return:
            None
        """
        if not os.path.isdir(self.__path_to_markdown_notes):
            os.makedirs(self.__path_to_markdown_notes)
        for file_name in os.listdir(self.__path_to_markdown_notes):
            file_name = os.path.join(self.__path_to_markdown_notes, file_name)
            if os.path.isfile(file_name):
                os.unlink(file_name)

    @staticmethod
    def __insert_blank_line_before_each_list(content: list[str]) -> list[str]:
        """Insert blank line before each Markdown list when it is needed by Misaka parser."""
        list_markers = ['* ', '- ', '+ ', '1. ']
        result = []
        for first, second in zip(content, content[1:]):
            result.append(first)
            if any([second.startswith(x) for x in list_markers]) and first:
                result.append('')
        result.append(content[-1])
        return result

    def copy_cell_content_to_markdown_file(self, cell: dict[str, Any]) -> None:
        """
        Extract content of the cell and save it as Markdown file in the specified directory.

        :param cell:
            Jupyter notebook cell to be processed
        :return:
            None
        """
        content = [line.rstrip('\n') for line in cell['source']]
        content = self.__insert_blank_line_before_each_list(content)
        note_title = content[0].lstrip('# ')
        file_name = compress(note_title)
        file_path = os.path.join(self.__path_to_markdown_notes, file_name) + '.md'
        with open(file_path, 'w') as destination_file:
            for line in content:  # pragma: no branch
                destination_file.write(line + '\n')


class TagCountsMaker:
    """
    Maker of TSV file with counts of tags.

    :param path_to_tsv_file:
        path to output TSV (tab-separated values) file
    """

    def __init__(self, path_to_tsv_file: str):
        """Initialize an instance."""
        self.__path_to_tsv_file = path_to_tsv_file
        self.__tag_counts = defaultdict(lambda: 0)

    def update_tags_counts(self, cell: dict[str, Any]) -> None:
        """
        Increase counters for cell tags.

        :param cell:
            Jupyter notebook cell to be processed
        :return:
            None
        """
        cell_tags = cell['metadata']['tags']
        for tag in cell_tags:
            self.__tag_counts[tag] += 1

    def write_tag_counts_to_tsv_file(self) -> None:
        """
        Write tag counts to TSV file.

        :return:
            None
        """
        sorted_tags_and_counts = sorted(
            self.__tag_counts.items(),
            key=lambda tag_and_count: (-tag_and_count[1], tag_and_count[0])
        )
        with open(self.__path_to_tsv_file, 'w') as destination_file:
            for tag, count in sorted_tags_and_counts:
                destination_file.write(f'{tag}\t{count}\n')


class TagToNotesDatabaseMaker:
    """
    Maker of SQLite database that maps a tag to a list of notes.

    Every table from the output DB has the name equal to the corresponding tag
    and stores IDs of notes in separate records.

    :param path_to_db:
        path to SQLite database;
        if this file already exists, it will be overwritten, else the file will be created
    """

    def __init__(self, path_to_db: str):
        """Initialize an instance."""
        self.__path_to_db = path_to_db
        self.__tag_to_notes = defaultdict(lambda: [])

    def update_mapping_of_tags_to_notes(self, cell: dict[str, Any]) -> None:
        """
        Add cell header to the lists corresponding to its tags.

        :param cell:
            Jupyter notebook cell to be processed
        :return:
            None
        """
        cell_header = cell['source'][0].rstrip('\n')
        cell_header = cell_header.lstrip('# ')
        cell_tags = cell['metadata']['tags'] + ['all_notes']
        for tag in cell_tags:
            self.__tag_to_notes[tag].append(cell_header)

    def write_tag_to_notes_mapping_to_db(self) -> None:
        """
        Write content of `self.tag_to_notes` to the target DB.

        :return:
            None
        """
        with closing(sqlite3.connect(self.__path_to_db)) as connection:
            with open_transaction(connection) as cursor:
                for k, v in self.__tag_to_notes.items():  # pragma: no branch
                    cursor.execute(
                        f"CREATE TABLE IF NOT EXISTS {k} (note_id VARCHAR)"
                    )
                    cursor.execute(
                        f"""
                        CREATE UNIQUE INDEX IF NOT EXISTS
                            {k}_index
                        ON
                            {k} (note_id)
                        """
                    )
                    cursor.execute(
                        f"DELETE FROM {k}"
                    )
                    for note_title in v:
                        cursor.execute(
                            f"INSERT INTO {k} (note_id) VALUES (?)",
                            (compress(note_title),)
                        )
            with closing(connection.cursor()) as cursor:
                cursor.execute('VACUUM')


def make_resources_for_single_field(
        ipynb_dir: str,
        markdown_dir: str,
        tag_counts_path: str,
        tag_to_notes_db_path: str
) -> None:
    """
    Make resources for a single directory representing a particular field of knowledge.

    :param ipynb_dir:
        path to existing directory with Jupyter notebooks
    :param markdown_dir:
        path to directory where Markdown files with notes should be created
    :param tag_counts_path:
        path to tag counts TSV file to be created
    :param tag_to_notes_db_path:
        path to SQLite DB file to be created
    :return:
        None
    """
    md_maker = MarkdownNotesMaker(markdown_dir)
    md_maker.provide_empty_directory()

    tag_counts_maker = TagCountsMaker(tag_counts_path)
    tag_to_notes_db_maker = TagToNotesDatabaseMaker(tag_to_notes_db_path)

    for cell in extract_cells(ipynb_dir):
        md_maker.copy_cell_content_to_markdown_file(cell)
        tag_counts_maker.update_tags_counts(cell)
        tag_to_notes_db_maker.update_mapping_of_tags_to_notes(cell)

    tag_counts_maker.write_tag_counts_to_tsv_file()
    tag_to_notes_db_maker.write_tag_to_notes_mapping_to_db()


def make_resources(notes_dir: str, resources_dir: str) -> None:
    """
    Make all resources.

    :param notes_dir:
        outer directory with notes in Jupyter format
    :param resources_dir:
        directory where resources are going to be created
    :return:
        None
    """
    for object_name in os.listdir(notes_dir):
        object_path = os.path.join(notes_dir, object_name)
        if not os.path.isdir(object_path) or object_name.startswith('.'):
            continue
        field = object_name
        nested_notes_dir = object_path
        make_resources_for_single_field(
            nested_notes_dir,
            os.path.join(resources_dir, field, MARKDOWN_DIR_NAME),
            os.path.join(resources_dir, field, TAG_COUNTS_FILE_NAME),
            os.path.join(resources_dir, field, TAG_TO_NOTES_DB_FILE_NAME)
        )


if __name__ == '__main__':
    make_resources(NOTES_DIR, RESOURCES_DIR)
