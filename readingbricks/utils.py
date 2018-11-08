"""
It is just a small module for auxiliary tools.

Author: Nikolay Lysenko
"""


import os
import json
import sqlite3
import hashlib
from contextlib import contextmanager
from typing import Dict, Generator, Any

# Note that there must be no dependencies other than Python built-ins,
# because this module is imported by scripts from `supplementaries`.


def extract_cells(path_to_dir: str) -> Generator[Dict[str, Any], None, None]:
    """
    Walk through directory and yield cells of notebooks from there.

    :param path_to_dir:
        path to source directory with Jupyter notebooks
    :yield:
        cells as dictionaries
    """
    file_names = [
        x for x in os.listdir(path_to_dir)
        if os.path.isfile(os.path.join(path_to_dir, x)) and not x.endswith('~')
    ]
    for file_name in file_names:
        with open(os.path.join(path_to_dir, file_name)) as source_file:
            cells = json.load(source_file)['cells']
            for cell in cells:
                yield cell


def compress(string: str, max_length: int = 64) -> str:
    """
    Compress a string to a string of restricted length.

    The function can be useful, because some filesystems and/or
    disk encryption tools impose restriction on maximum length of
    a filename.

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
        conn: sqlite3.Connection
) -> Generator[sqlite3.Cursor, None, None]:
    """Open transaction to SQLite database within a context."""
    cur = conn.cursor()
    cur.execute('BEGIN TRANSACTION')
    try:
        yield cur
    except Exception as e:  # pragma: no cover
        print(e)
        cur.execute('ROLLBACK')
    else:
        cur.execute('COMMIT')
    finally:
        cur.close()
