"""
This module contains utilities for parsing user queries
and for selecting matching notes.

@author: Nikolay Lysenko
"""


import sqlite3
import contextlib
import string
from typing import List

import pyparsing as pp


class LogicalQueriesHandler:
    """
    A class that converts query of a special form into SQL
    statements, interacts with a database, and returns list of
    matching notes.

    Valid query can involve only tags, binary logical operators
    (i.e., AND and OR), parentheses, and spaces.
    An example of a query that can be processed by this class:
    "neural_networks AND (problem_setup OR bayesian_methods)".
    Response to this query is a list of all notes tagged with
    "neural networks" tag and at least one of "problem_setup" and
    "bayesian_methods" tags.

    :param path_to_db:
        absolute path to SQLite database with tables representing tags
        and rows representing notes
    """

    def __init__(self, path_to_db: str):
        self.__path_to_db = path_to_db

    @staticmethod
    def __infer_precedence(user_query: str) -> str:
        # Put square brackets that indicates precedence of operations.
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

    @staticmethod
    def __create_tmp_table(leaf: List[str], cur: sqlite3.Cursor) -> str:
        # Create temporary table for a single leaf.
        # Here, leaf means a part of the query with no nested parts in it
        # and a part means something that is inside square brackets.
        operator = leaf[1]
        operands = leaf[::2]
        if operator == 'AND':
            operands_and_aliases = list(zip(operands, string.ascii_lowercase))
            query = (
                f"""
                SELECT
                    a.note_id
                FROM
                    {operands[0]} a
                """
                + '\n'.join(
                    [
                        f"""
                        JOIN
                        {operand} {alias}
                        ON
                            a.note_id = {alias}.note_id
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
                            note_id
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
                {tmp_table_name}_index ON {tmp_table_name} (note_id)
            """
        )
        return f"'{tmp_table_name}'"

    def __replace_leaf_with_tmp_table(
            self,
            parsed_query: str,
            cur: sqlite3.Cursor
            ) -> str:
        # Create a temporary table for a single leaf and return a query
        # where this leaf is replaced with the name of the temporary table.
        parts = parsed_query.split(']')
        left_part = parts.pop(0)
        left_parts = left_part.split('[')
        leaf = left_parts.pop()
        pre_leaf = '['.join(left_parts)
        post_leaf = ']'.join(parts)
        leaf_as_list = leaf.replace("'", "").split(', ')
        tmp_table_name = self.__create_tmp_table(leaf_as_list, cur)
        return pre_leaf + tmp_table_name + post_leaf

    def find_all_relevant_notes(self, user_query: str) -> List[str]:
        """
        Return list of notes that match the query.

        :param user_query:
            expression with tags as operands, AND and OR operators,
            and parentheses. For example:
            "neural_networks AND (problem_setup OR bayesian_methods)"
        :return:
            list of matching notes
        """
        parsed_query = self.__infer_precedence(user_query)
        with contextlib.closing(sqlite3.connect(self.__path_to_db)) as conn:
            with contextlib.closing(conn.cursor()) as cur:
                while ']' in parsed_query:
                    parsed_query = self.__replace_leaf_with_tmp_table(
                        parsed_query, cur
                    )
                tmp_table_name = parsed_query.strip("'")
                cur.execute(f"SELECT note_id FROM {tmp_table_name}")
                query_result = cur.fetchall()
                note_ids = [x[0] for x in query_result]
        return note_ids
