"""
This script updates SQLite database for Flask application.
This task is not done by pre-commit hook, because it is not a good
practice to store binary files in a Git repository and so
the file managed by the script differs from files managed by
pre-commit hook.

@author: Nikolay Lysenko
"""


import sqlite3
from collections import defaultdict
from typing import Dict, Any
from contextlib import contextmanager

from readingbricks.ipynb_utils import extract_cells
from readingbricks.path_configuration import (
    get_path_to_ipynb_notes, get_path_to_db
)


def update_mapping_of_tags_to_notes(
        tag_to_notes: defaultdict, cell: Dict[str, Any]
        ) -> defaultdict:
    """
    Store cell header in lists that relates to its tags.
    """
    cell_header = cell['source'][0].rstrip('\n')
    cell_header = cell_header.lstrip('## ')
    cell_tags = cell['metadata']['tags']
    for tag in cell_tags:
        tag_to_notes[tag].append(cell_header)
    return tag_to_notes


@contextmanager
def open_transaction(conn: sqlite3.Connection):
    """
    An analogue of `contextlib.closing` for `sqlite3.Connection`.
    """
    cur = conn.cursor()
    cur.execute('BEGIN TRANSACTION')
    try:
        yield cur
    except Exception as e:
        print(e)
        cur.execute('ROLLBACK')
    else:
        cur.execute('COMMIT')
    finally:
        cur.close()


def write_tag_to_notes_mapping_to_db(
        tag_to_notes: defaultdict, absolute_path: str
        ) -> type(None):
    """
    Overwrite with content of `tag_to_notes` content of
    SQLite database specified in `absolute_path`.
    """
    conn = sqlite3.connect(absolute_path)
    with open_transaction(conn) as cur:
        for k, v in tag_to_notes.items():
            cur.execute(
                f"CREATE TABLE IF NOT EXISTS {k} (note_title VARCHAR)"
            )
            cur.execute(
                f"""
                CREATE UNIQUE INDEX IF NOT EXISTS {k}_index ON {k} (note_title)
                """
            )
            cur.execute(
                f"DELETE FROM {k}"
            )
            for note_title in v:
                cur.execute(
                    f"INSERT INTO {k} (note_title) VALUES (?)",
                    (note_title,)
                )
    cur = conn.cursor()
    cur.execute('VACUUM')
    cur.close()
    conn.close()


def create_or_refresh_db() -> type(None):
    """
    Create SQLite database if it does not exist or update it else.
    """
    absolute_paths = {
        'source': get_path_to_ipynb_notes(),
        'destination': get_path_to_db()
    }
    tag_to_notes = defaultdict(lambda: [])
    for cell in extract_cells(absolute_paths['source']):
        tag_to_notes = update_mapping_of_tags_to_notes(tag_to_notes, cell)
    write_tag_to_notes_mapping_to_db(
        tag_to_notes, absolute_paths['destination']
    )


if __name__ == '__main__':
    create_or_refresh_db()
