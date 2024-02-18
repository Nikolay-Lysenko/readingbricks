"""
Provide auxiliary tools.

Author: Nikolay Lysenko
"""


import os
import hashlib
import json
import sqlite3
from contextlib import contextmanager
from typing import Any, Generator

# Note that there must be no dependencies other than Python built-ins,
# because this module is imported by scripts that are used in Git hooks.


def extract_cells(path_to_dir: str) -> Generator[dict[str, Any], None, None]:
    """
    Walk through directory and yield cells of notebooks from there.

    :param path_to_dir:
        path to source directory with Jupyter notebooks
    :yield:
        cells as dictionaries
    """
    for file_name in sorted(os.listdir(path_to_dir)):
        file_path = os.path.join(path_to_dir, file_name)
        if not os.path.isfile(file_path) or not file_name.endswith('.ipynb'):
            continue
        with open(file_path) as source_file:
            cells = json.load(source_file)['cells']
            for cell in cells:  # pragma: no branch
                yield cell


def compress(string: str, max_length: int = 64) -> str:
    """
    Compress a string to a string of restricted length.

    The function can be useful, because some filesystems and/or disk encryption tools
    impose restriction on maximum length of a filename.

    :param string:
        string to be compressed
    :param max_length:
        maximum length of output, default is 64
    :return:
        compressed string which is a truncated hash of input string
    """
    hashed_string = hashlib.sha256(string.encode('utf-8')).hexdigest()
    result = hashed_string[:max_length]
    return result


@contextmanager
def open_transaction(
        connection: sqlite3.Connection
) -> Generator[sqlite3.Cursor, None, None]:
    """
    Open transaction to SQLite database within a context.

    :param connection:
        connection to SQLite database
    :return:
        cursor such that changes made with it are either committed or rolled back
    """
    cursor = connection.cursor()
    cursor.execute('BEGIN TRANSACTION')
    try:
        yield cursor
    except Exception as e:  # pragma: no cover
        print(e)
        cursor.execute('ROLLBACK')
    else:
        cursor.execute('COMMIT')
    finally:
        cursor.close()
