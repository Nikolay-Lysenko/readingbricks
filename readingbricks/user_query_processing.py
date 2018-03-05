"""
This module contains utilities for parsing user queries
and for selecting matching notes.

@author: Nikolay Lysenko
"""


import sqlite3
import string
import contextlib
from typing import List

import pyparsing as pp

from readingbricks.path_configuration import get_path_to_db


def infer_precedence(user_query: str) -> str:
    """
    Put square brackets that indicates precedence of operations.
    """
    extra_chars = pp.srange(r"[\0x80-\0x7FF]")  # Support Cyrillic letters.
    tag = pp.Word(pp.alphas + '_' + extra_chars)
    parser = pp.operatorPrecedence(
        tag,
        [
            ("NOT", 1, pp.opAssoc.RIGHT),  # Not supported further.
            ("AND", 2, pp.opAssoc.LEFT),
            ("OR", 2, pp.opAssoc.LEFT)
        ]
    )
    parsed_expression = parser.parseString(user_query)[0]
    return str(parsed_expression)


def create_tmp_table(leaf: List[str], cur: sqlite3.Cursor) -> str:
    """
    Create temporary table for a single leaf operation.
    """
    operator = leaf[1]
    operands = leaf[::2]
    if operator == 'AND':
        operands_and_aliases = list(zip(operands, string.ascii_lowercase))
        query = (
            f"""
            SELECT
                a.note_title
            FROM
                {operands[0]} a
            """
            + '\n'.join(
                [
                    f"""
                    JOIN
                    {operand} {alias}
                    ON
                        a.note_title = {alias}.note_title
                    """
                    for operand, alias in operands_and_aliases[1:]
                ]
            )
        )
    elif operator == 'OR':
        query = (
            "UNION".join(
                [
                    f"""
                    SELECT
                        note_title
                    FROM
                        {operand}
                    """
                    for operand in operands
                ]
            )
        )
    else:
        raise ValueError(f"Unknown operator: {operator}")
    tmp_table_name = '_'.join(leaf)
    cur.execute(f"CREATE TEMP TABLE {tmp_table_name} AS {query}")
    cur.execute(
        f"""
        CREATE UNIQUE INDEX IF NOT EXISTS
            {tmp_table_name}_index ON {tmp_table_name} (note_title)
        """
    )
    return f"'{tmp_table_name}'"


def replace_leaf_with_tmp_table(parsed_query: str, cur: sqlite3.Cursor) -> str:
    """
    Create temporary table for a single operation and replace
    this operation with name of the temporary table.
    """
    parts = parsed_query.split(']')
    left_part = parts.pop(0)
    left_parts = left_part.split('[')
    leaf = left_parts.pop()
    pre_leaf = '['.join(left_parts)
    post_leaf = ']'.join(parts)
    leaf_as_list = leaf.replace("'", "").split(', ')
    tmp_table_name = create_tmp_table(leaf_as_list, cur)
    return pre_leaf + tmp_table_name + post_leaf


def find_all_relevant_notes(user_query: str) -> List[str]:
    """
    Return list of notes that match the query.
    An example of a query that can be processed by this function:
    "neural_networks AND (problem_setup OR bayesian_methods)"
    """
    parsed_query = infer_precedence(user_query)
    with contextlib.closing(sqlite3.connect(get_path_to_db())) as conn:
        with contextlib.closing(conn.cursor()) as cur:
            while ']' in parsed_query:
                parsed_query = replace_leaf_with_tmp_table(parsed_query, cur)
            tmp_table_name = parsed_query.strip("'")
            cur.execute(f"SELECT note_title FROM {tmp_table_name}")
            query_result = cur.fetchall()
            note_titles = [x[0] for x in query_result]
    return note_titles
