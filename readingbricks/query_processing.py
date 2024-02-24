"""
Parse tag-based user queries and select matching notes.

Author: Nikolay Lysenko
"""


import sqlite3
import string
from contextlib import closing

import pyparsing as pp
from nltk.stem.snowball import SnowballStemmer

from readingbricks.constants import LANGUAGES_FOR_STEMMER
from readingbricks.utils import open_transaction, standardize_string


class TagQueriesProcessor:
    """
    Processor of tag-based queries that returns hashed titles of matching notes.

    The execution pipeline looks like this:
    * a query of a proper form is converted to SQL statement,
    * database interaction starts,
    * list of matching notes (identified by hashed titles) is returned as a result.

    Valid query can involve only these entities:
    * tags,
    * logical operators (i.e., AND, OR, and NOT),
    * parentheses,
    * spaces.

    An example of a query that can be processed by this class:
    "neural_networks AND (problem_setup OR bayesian_methods)".

    Response to this query is a list of all notes tagged with "neural networks" tag
    and at least one of "problem_setup" and "bayesian_methods" tags.

    :param path_to_db:
        absolute path to SQLite database with tables representing tags and rows representing notes
    """

    def __init__(self, path_to_db: str):
        """Initialize an instance."""
        self.__path_to_db = path_to_db

    @staticmethod
    def __infer_precedence(query: str) -> str:
        """Put square brackets that indicate precedence of operations."""
        extra_chars = pp.srange(r"[\0x80-\0x7FF]")  # Support Cyrillic letters.
        tag = pp.Word(pp.alphas + '_' + extra_chars)
        parser = pp.infix_notation(
            tag,
            [
                ("NOT", 1, pp.OpAssoc.RIGHT),
                ("AND", 2, pp.OpAssoc.LEFT),
                ("OR", 2, pp.OpAssoc.LEFT)
            ]
        )
        parsed_expression = parser.parse_string(query)[0]
        return str(parsed_expression)

    @staticmethod
    def __compose_sql_query(operator: str, operands: list[str]) -> str:
        """Turn logical operation into SQL query that performs it."""
        if operator == 'AND':
            operands_and_aliases = list(zip(operands, string.ascii_lowercase))
            query = (
                f'''
                SELECT
                    a.title_hash
                FROM
                    {operands[0]} a
                '''
                + '\n'.join(
                    [
                        f'''
                        JOIN
                        {operand} {alias}
                        ON
                            a.title_hash = {alias}.title_hash
                        '''
                        for operand, alias in operands_and_aliases[1:]
                    ]
                )
            )
        elif operator == 'OR':
            query = (
                "UNION".join(
                    [
                        f'''
                        SELECT
                            title_hash
                        FROM
                            {operand}
                        '''
                        for operand in operands
                    ]
                )
            )
        elif operator == 'NOT':
            query = (
                f'''
                SELECT
                    *
                FROM
                    all_notes a
                WHERE
                    NOT EXISTS(
                        SELECT
                            *
                        FROM
                            {operands[0]} b
                        WHERE
                            a.title_hash = b.title_hash
                    )
                '''
            )
        else:
            raise ValueError(f"Unknown operator: {operator}")
        return query

    def __create_tmp_table(self, leaf: list[str], cur: sqlite3.Cursor) -> str:
        """
        Create temporary table for a single leaf.

        Here, leaf means a part of the parsed user query without any nested parts in it
        and a part means anything that is inside square brackets.
        """
        if 'NOT' in leaf:
            operator = 'NOT'
            operands = [leaf[1]]
        else:
            operator = leaf[1]
            operands = leaf[::2]
        query = self.__compose_sql_query(operator, operands)
        tmp_table_name = '_'.join(leaf)
        cur.execute(f"CREATE TEMP TABLE {tmp_table_name} AS {query}")
        cur.execute(
            f'''
            CREATE UNIQUE INDEX IF NOT EXISTS {tmp_table_name}_index
            ON {tmp_table_name} (title_hash)
            '''
        )
        return f"'{tmp_table_name}'"

    def __replace_leaf_with_tmp_table(
            self,
            parsed_query: str,
            cur: sqlite3.Cursor
    ) -> str:
        """Return a query where a leaf is replaced with the name of the table created for it."""
        parts = parsed_query.split(']')
        left_part = parts.pop(0)
        left_parts = left_part.split('[')
        leaf = left_parts.pop()
        pre_leaf = '['.join(left_parts)
        post_leaf = ']'.join(parts)
        leaf_as_list = leaf.replace("'", "").split(', ')
        tmp_table_name = self.__create_tmp_table(leaf_as_list, cur)
        return pre_leaf + tmp_table_name + post_leaf

    def find_notes(self, query: str) -> list[str]:
        """
        Return list of hashed titles for notes that match the query.

        :param query:
            expression with AND, OR, and NOT operators,
            tags as operands, and parentheses. For example:
            "neural_networks AND (problem_setup OR bayesian_methods)"
        :return:
            hashed titles of matching notes
        """
        parsed_query = self.__infer_precedence(query)
        with closing(sqlite3.connect(self.__path_to_db)) as connection:
            with closing(connection.cursor()) as cursor:
                while ']' in parsed_query:
                    parsed_query = self.__replace_leaf_with_tmp_table(parsed_query, cursor)
                tmp_table_name = parsed_query.strip("'")
                cursor.execute(
                    f"""
                    SELECT
                        a.title_hash
                    FROM
                        {tmp_table_name} a
                        JOIN
                        precedences b
                        ON
                            a.title_hash = b.title_hash
                    ORDER BY
                        precedence
                    """
                )
                query_result = cursor.fetchall()
                hashed_titles = [x[0] for x in query_result]  # pragma: no branch
        return hashed_titles


class TfIdfQueriesProcessor:
    """
    Processor of text queries that returns hashed titles of matching notes sorted by TF-IDF.

    :param path_to_db:
        absolute path to SQLite database with tables storing TF and IDF statistics
    :param language:
        main language of notes
    """

    def __init__(self, path_to_db: str, language: str):
        """Initialize an instance."""
        self.__path_to_db = path_to_db
        self.__stemmer = SnowballStemmer(LANGUAGES_FOR_STEMMER[language])

    def find_notes(self, query: str) -> list[str]:
        """
        Return list of hashed titles for notes that match the query.

        :param query:
            query in the appropriate natural language
        :return:
            hashed titles of matching notes
        """
        query = standardize_string(query)
        words = query.split()
        terms = {self.__stemmer.stem(word) for word in words}
        with closing(sqlite3.connect(self.__path_to_db)) as connection:
            with open_transaction(connection) as cursor:
                cursor.execute(
                    "CREATE TEMP TABLE query (term VARCHAR)"
                )
                cursor.execute(
                    "CREATE UNIQUE INDEX IF NOT EXISTS query_index ON query (term)"
                )
                for term in terms:
                    cursor.execute(
                        "INSERT INTO query (term) VALUES (?)",
                        (term,)
                    )
                cursor.execute(
                    """
                    SELECT
                        title_hash,
                        SUM(log_tf * log_idf) AS tf_idf
                    FROM
                        query a
                        JOIN
                        tf b
                        ON
                            a.term = b.term
                        JOIN
                        idf c
                        ON
                            a.term = c.term
                    GROUP BY
                        title_hash
                    ORDER BY
                        tf_idf DESC
                    """
                )
                query_result = cursor.fetchall()
                hashed_titles = [x[0] for x in query_result]  # pragma: no branch
        return hashed_titles


class QueriesProcessor:
    """
    Processor of composite queries which may have natural language part and tag expression part.

    :param path_to_tag_to_notes_db:
        absolute path to SQLite database with tables representing tags and rows representing notes
    :param path_to_tf_idf_db:
        absolute path to SQLite database with tables storing TF and IDF statistics
    :param language:
        main language of notes
    """

    parts_separator = "tags:"

    def __init__(self, path_to_tag_to_notes_db: str, path_to_tf_idf_db: str, language: str):
        """Initialize an instance."""
        self.__tag_queries_processor = TagQueriesProcessor(path_to_tag_to_notes_db)
        self.__tf_idf_queries_processor = TfIdfQueriesProcessor(path_to_tf_idf_db, language)

    def __split_query(self, query: str) -> tuple[str, str]:
        """Split query into two parts."""
        split_query = query.split(self.parts_separator)
        natural_language_part = split_query[0].strip()
        tags_part = split_query[1].strip() if len(split_query) > 1 else ''
        return natural_language_part, tags_part

    def find_notes(self, query: str) -> list[str]:
        """
        Return list of hashed titles for notes that match the query.

        :param query:
            composite query which may have natural language part and tag expression part
        :return:
            hashed titles of matching notes
        """
        natural_language_part, tags_part = self.__split_query(query)
        if natural_language_part and tags_part:
            tf_idf_notes = self.__tf_idf_queries_processor.find_notes(natural_language_part)
            tag_notes = self.__tag_queries_processor.find_notes(tags_part)
            return [x for x in tf_idf_notes if x in tag_notes]
        if natural_language_part:
            tf_idf_notes = self.__tf_idf_queries_processor.find_notes(natural_language_part)
            return tf_idf_notes
        if tags_part:
            tag_notes = self.__tag_queries_processor.find_notes(tags_part)
            return tag_notes
        else:
            return []
