"""
Test `utils` module.

Author: Nikolay Lysenko
"""


import os

import pytest

from readingbricks.utils import extract_cells


@pytest.mark.parametrize(
    "tag, expected",
    [
        (
            # `tag`
            "letters",
            # `expected`
            [
                ['## A\n', '\n', 'A'],
                ['## B\n', '\n', 'B'],
                [
                    '## C\n', '\n', 'C:\n', '* c\n', '* _c_\n', '* $c$\n', '\n',
                    '[link](__home_url__/notes/B)'
                ],
                ['## D\n', '\n', 'D'],
            ]
        ),
        (
            # `tag`
            "digits",
            # `expected`
            [
                ['## 1\n', '\n', '1'],
                ['## 2\n', '\n', '2'],
            ]
        ),
    ]
)
def test_extract_cells(tag: str, expected: list[list[str]]) -> None:
    """Test `extract_cells` function."""
    path = os.path.join(os.path.dirname(__file__), 'notes', 'digits_and_letters')
    result = [cell['source'] for cell in extract_cells(path) if tag in cell['metadata']['tags']]
    assert result == expected
