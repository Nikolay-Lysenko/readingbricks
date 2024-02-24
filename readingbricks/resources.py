"""
Make resources.

Here, a resource is anything that has below properties:
1) it is used by the Flask application;
2) it should not be added to Git repository.

Author: Nikolay Lysenko
"""


import os
import sqlite3
from collections import Counter, defaultdict
from contextlib import closing
from math import log
from nltk.stem.snowball import SnowballStemmer
from typing import Any

from readingbricks.constants import (
    LANGUAGES_FOR_STEMMER,
    MARKDOWN_DIR_NAME,
    TAG_COUNTS_FILE_NAME,
    TAG_TO_NOTES_DB_FILE_NAME,
    TF_IDF_DB_FILE_NAME
)
from readingbricks.default_settings import (
    LANGUAGE,
    NOTES_DIR,
    RESOURCES_DIR,
)
from readingbricks.utils import compress, extract_cells, open_transaction, standardize_string


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
    def __insert_blank_line_before_each_list(contents: list[str]) -> list[str]:
        """Insert blank line before each Markdown list when it is needed by Misaka parser."""
        list_markers = ['* ', '- ', '+ ', '1. ']
        result = []
        for first, second in zip(contents, contents[1:]):
            result.append(first)
            if any([second.startswith(x) for x in list_markers]) and first:
                result.append('')
        result.append(contents[-1])
        return result

    def copy_cell_contents_to_markdown_file(self, cell: dict[str, Any]) -> None:
        """
        Extract contents of the cell and save it as Markdown file in the specified directory.

        :param cell:
            Jupyter notebook cell to be processed
        :return:
            None
        """
        contents = [line.rstrip('\n') for line in cell['source']]
        contents = self.__insert_blank_line_before_each_list(contents)
        note_title = contents[0].lstrip('# ')
        file_name = compress(note_title)
        file_path = os.path.join(self.__path_to_markdown_notes, file_name) + '.md'
        with open(file_path, 'w') as destination_file:
            for line in contents:  # pragma: no branch
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

    Tables from the output DB have the names equal to the corresponding tags
    and store hashed titles of notes in separate records.

    Also, there is an extra table mapping hashed title to relative precedence of its note.

    :param path_to_db:
        path to SQLite database;
        if this file already exists, it will be overwritten, else the file will be created
    """

    def __init__(self, path_to_db: str):
        """Initialize an instance."""
        self.__path_to_db = path_to_db
        self.__tag_to_title_hashes = defaultdict(list)
        self.__title_hash_to_precedence = {}

    def update_mappings(self, cell: dict[str, Any], precedence: int) -> None:
        """
        Update internal mappings on a single cell.

        Namely, do the following:
        * add hashed cell header to the lists corresponding to tags of the cell;
        * save precedence of the cell.

        :param cell:
            Jupyter notebook cell to be processed
        :param precedence:
            precedence of the cell relatively to other cells
            (it is used on tag pages and on search results by logical queries)
        :return:
            None
        """
        cell_header = cell['source'][0].rstrip('\n')
        cell_header = cell_header.lstrip('# ')
        hashed_header = compress(cell_header)
        cell_tags = cell['metadata']['tags'] + ['all_notes']
        for tag in cell_tags:
            self.__tag_to_title_hashes[tag].append(hashed_header)
        self.__title_hash_to_precedence[hashed_header] = precedence

    def write_mappings_to_db(self) -> None:
        """
        Create all necessary tables and indices in the target DB.

        :return:
            None
        """
        with closing(sqlite3.connect(self.__path_to_db)) as connection:
            with open_transaction(connection) as cursor:
                for k, v in self.__tag_to_title_hashes.items():  # pragma: no branch
                    cursor.execute(
                        f"CREATE TABLE IF NOT EXISTS {k} (title_hash VARCHAR)"
                    )
                    cursor.execute(
                        f"CREATE UNIQUE INDEX IF NOT EXISTS {k}_index ON {k} (title_hash)"
                    )
                    cursor.execute(
                        f"DELETE FROM {k}"
                    )
                    for title_hash in v:
                        cursor.execute(
                            f"INSERT INTO {k} (title_hash) VALUES (?)",
                            (title_hash,)
                        )

                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS precedences (title_hash VARCHAR, precedence INT)"
                )
                cursor.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS precedences_index "
                    "ON precedences (title_hash)"
                )
                cursor.execute(
                    "DELETE FROM precedences"
                )
                for k, v in self.__title_hash_to_precedence.items():
                    cursor.execute(
                        "INSERT INTO precedences (title_hash, precedence) VALUES (?, ?)",
                        (k, v)
                    )

            with closing(connection.cursor()) as cursor:
                cursor.execute('VACUUM')


class TfIdfDatabaseMaker:
    """
    Maker of SQLite database with statistics involved in TF-IDF calculation.

    :param path_to_db:
        path to SQLite database;
        if this file already exists, it will be overwritten, else the file will be created
    :param language:
        main language of notes
    """

    def __init__(self, path_to_db: str, language: str = 'ru'):
        """Initialize an instance."""
        self.__path_to_db = path_to_db
        self.__stemmer = SnowballStemmer(LANGUAGES_FOR_STEMMER[language])
        self.__title_hash_to_term_counts = {}
        self.__term_to_count_of_notes = defaultdict(int)
        self.__n_notes = 0

    def update_statistics(self, cell: dict[str, Any]) -> None:
        """
        Update statistics on a single cell.

        :param cell:
            Jupyter notebook cell to be processed
        :return:
            None
        """
        cell_header = cell['source'][0].rstrip('\n')
        cell_header = cell_header.lstrip('# ')
        hashed_header = compress(cell_header)

        contents = ''.join(cell['source'])
        standardized_contents = standardize_string(contents)
        words = standardized_contents.split()
        terms = [self.__stemmer.stem(word) for word in words]

        self.__title_hash_to_term_counts[hashed_header] = Counter(terms)
        for term in set(terms):
            self.__term_to_count_of_notes[term] += 1
        self.__n_notes += 1

    def write_statistics_to_db(self) -> None:
        """
        Create all necessary tables and indices in the target DB.

        :return:
            None
        """
        with closing(sqlite3.connect(self.__path_to_db)) as connection:
            with open_transaction(connection) as cursor:
                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS tf (term VARCHAR, title_hash VARCHAR, log_tf INT)"
                )
                cursor.execute(
                    "CREATE INDEX IF NOT EXISTS tf_index ON tf (term)"
                )
                cursor.execute(
                    "DELETE FROM tf"
                )
                for title_hash, counter in self.__title_hash_to_term_counts.items():
                    for term, count in counter.items():
                        cursor.execute(
                            "INSERT INTO tf (term, title_hash, log_tf) VALUES (?, ?, ?)",
                            (term, title_hash, log(1 + count))
                        )

                cursor.execute(
                    "CREATE TABLE IF NOT EXISTS idf (term VARCHAR, log_idf REAL)"
                )
                cursor.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS idf_index ON idf (term)"
                )
                cursor.execute(
                    "DELETE FROM idf"
                )
                for term, n_notes in self.__term_to_count_of_notes.items():
                    cursor.execute(
                        "INSERT INTO idf (term, log_idf) VALUES (?, ?)",
                        (term, log(self.__n_notes / n_notes))
                    )

            with closing(connection.cursor()) as cursor:
                cursor.execute('VACUUM')


def make_resources_for_single_field(
        ipynb_dir: str,
        markdown_dir: str,
        tag_counts_path: str,
        tag_to_notes_db_path: str,
        tf_idf_db_path: str,
        stemmer_language: str
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
        path to tags SQLite DB file to be created
    :param tf_idf_db_path:
        path to TF-IDF SQLite DB file to be created
    :param stemmer_language:
        language for stemmer used in TF-IDF statistics calculation
    :return:
        None
    """
    md_maker = MarkdownNotesMaker(markdown_dir)
    md_maker.provide_empty_directory()

    tag_counts_maker = TagCountsMaker(tag_counts_path)
    tag_to_notes_db_maker = TagToNotesDatabaseMaker(tag_to_notes_db_path)
    tf_idf_maker = TfIdfDatabaseMaker(tf_idf_db_path, stemmer_language)

    for precedence, cell in enumerate(extract_cells(ipynb_dir)):
        md_maker.copy_cell_contents_to_markdown_file(cell)
        tag_counts_maker.update_tags_counts(cell)
        tag_to_notes_db_maker.update_mappings(cell, precedence)
        tf_idf_maker.update_statistics(cell)

    tag_counts_maker.write_tag_counts_to_tsv_file()
    tag_to_notes_db_maker.write_mappings_to_db()
    tf_idf_maker.write_statistics_to_db()


def make_resources(notes_dir: str, resources_dir: str, stemmer_language: str) -> None:
    """
    Make all resources.

    :param notes_dir:
        outer directory with notes in Jupyter format
    :param resources_dir:
        directory where resources are going to be created
    :param stemmer_language:
        language for stemmer used in TF-IDF statistics calculation
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
            os.path.join(resources_dir, field, TAG_TO_NOTES_DB_FILE_NAME),
            os.path.join(resources_dir, field, TF_IDF_DB_FILE_NAME),
            stemmer_language
        )


if __name__ == '__main__':
    make_resources(NOTES_DIR, RESOURCES_DIR, LANGUAGE)
