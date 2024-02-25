"""
Test `views` module.

Author: Nikolay Lysenko
"""


import flask.testing
import pytest


TITLE_TEMPLATE = '<h2><a href="http://localhost/{field}/notes/{title}">{title}</a></h2>'


def test_root_page(test_client: flask.testing.FlaskClient) -> None:
    """Test root page."""
    result = test_client.get('/').data.decode('utf-8')
    assert "Digits & Letters" in result
    assert "lorem_ipsum" in result
    assert "?" in result


def test_info_page(test_client: flask.testing.FlaskClient) -> None:
    """Test page with info about the project."""
    result = test_client.get('/about').data.decode('utf-8')
    assert "ReadingBricks - О проекте" in result
    assert "/" in result


@pytest.mark.parametrize(
    "field, included_patterns",
    [
        ("digits_and_letters", ["letters (4)", "digits (2)", "list (1)"]),
        ("lorem_ipsum", ["lorem_ipsum (2)"]),
    ]
)
def test_field_page(
        test_client: flask.testing.FlaskClient, field: str, included_patterns: list[str]
) -> None:
    """Test field page."""
    result = test_client.get(f"/{field}").data.decode('utf-8')
    assert "/" in result
    assert "?" in result
    for pattern in included_patterns:
        assert pattern in result


@pytest.mark.parametrize(
    "url",
    [
        "/non_existing",
        "/digits_and_letters/notes",
        "/digits_and_letters/tags",
        "/digits_and_letters/nots/1",
        "/digits_and_letters/notes/5",
        "/digits_and_letters/tags/alphanumeric",
    ]
)
def test_page_not_found(test_client: flask.testing.FlaskClient, url: str) -> None:
    """Test that a placeholder page is rendered if invalid URL is entered."""
    response = test_client.get(url)
    result = response.data.decode('utf-8')
    status_code = response.status_code
    assert '<title>Страница не найдена</title>' in result
    assert status_code == 404


@pytest.mark.parametrize(
    "url, included_patterns, absent_patterns",
    [
        (
            # `url`
            "/digits_and_letters/notes/C",
            # `included_patterns`
            [
                "C:",
                "<li><p><em>c</em></p></li>",
                "<li><p>\\(c\\)</p></li>",
                '<a href="http://localhost/digits_and_letters/notes/B">link</a>',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='C'),
            ],
            # `absent_patterns`
            [
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A'),
            ],
        ),
    ]
)
def test_note_page(
        test_client: flask.testing.FlaskClient,
        url: str,
        included_patterns: list[str],
        absent_patterns: list[str]
) -> None:
    """Test page with a single note."""
    result = test_client.get(url).data.decode('utf-8')
    assert "/" in result
    assert "⌂" in result
    assert "?" in result
    for pattern in included_patterns:
        assert pattern in result
    for pattern in absent_patterns:
        assert pattern not in result


@pytest.mark.parametrize(
    "url, included_patterns, absent_patterns",
    [
        (
            # `url`
            "/digits_and_letters/tags/digits",
            # `included_patterns`
            [
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='1')
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='C')
            ],
        ),
        (
            # `url`
            "/digits_and_letters/tags/list",
            # `included_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='C')
            ],
            # `absent_patterns`
            [
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='B')
            ],
        ),
    ]
)
def test_tag_page(
        test_client: flask.testing.FlaskClient,
        url: str,
        included_patterns: list[str],
        absent_patterns: list[str]
) -> None:
    """Test page with all notes tagged with a specified tag."""
    result = test_client.get(url).data.decode('utf-8')
    assert "/" in result
    assert "⌂" in result
    assert "?" in result
    for pattern in included_patterns:
        assert pattern in result
    for pattern in absent_patterns:
        assert pattern not in result


@pytest.mark.parametrize(
    "field, query, included_patterns, absent_patterns",
    [
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: list AND letters",
            # `included_patterns`
            [
                'C', '<li><p><em>c</em></p></li>', '<li><p>\\(c\\)</p></li>'
            ],
            # `absent_patterns`
            [
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='1')
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: list AND digits",
            # `included_patterns`
            [
                "<h2>Ничего не найдено</h2>"
            ],
            # `absent_patterns`
            [
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='B')
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: list OR letters",
            # `included_patterns`
            [
                '<li><p><em>c</em></p></li>',
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A'),
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='1')
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: list OR digits",
            # `included_patterns`
            [
                '<li><p><em>c</em></p></li>',
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='1'),
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A')
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: NOT list",
            # `included_patterns`
            [
                '<p>1</p>',
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A'),
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='C')
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: NOT letters",
            # `included_patterns`
            [
                '<p>2</p>',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='1'),
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A')
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: (list AND letters) OR (digits AND letters)",
            # `included_patterns`
            [
                '<li><p><em>c</em></p></li>',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='C'),
            ],
            # `absent_patterns`
            [
                '<div id="table_of_contents">',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A'),
                TITLE_TEMPLATE.format(field='digits_and_letters', title='B'),
                TITLE_TEMPLATE.format(field='digits_and_letters', title='1'),
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: (list AND letters) AND ((digits OR letters OR list) OR list)",
            # `included_patterns`
            [
                '<li><p><em>c</em></p></li>',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='C'),
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A'),
                TITLE_TEMPLATE.format(field='digits_and_letters', title='B'),
                TITLE_TEMPLATE.format(field='digits_and_letters', title='1'),
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: digits OR NOT (letters AND NOT list)",
            # `included_patterns`
            [
                '<li><p><em>c</em></p></li>',
                TITLE_TEMPLATE.format(field='digits_and_letters', title='1'),
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A'),
                TITLE_TEMPLATE.format(field='digits_and_letters', title='D'),
            ],
        ),
        (
            # `field`
            "digits_and_letters",
            # `query`
            "tags: (list AND letters) AND ((digits OR letters OR list) OR lists)",
            # `included_patterns`
            [
                '<h2>Запрос не может быть обработан</h2>',
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='digits_and_letters', title='A'),
                TITLE_TEMPLATE.format(field='digits_and_letters', title='B'),
                TITLE_TEMPLATE.format(field='digits_and_letters', title='C'),
            ],
        ),
    ]
)
def test_tag_query_page(
        test_client: flask.testing.FlaskClient,
        field: str,
        query: str,
        included_patterns: list[str],
        absent_patterns: list[str]
) -> None:
    """Test page with results of search by tags."""
    result = test_client.post(f'/{field}/query', data={'query': query}).data.decode('utf-8')
    assert "/" in result
    assert "⌂" in result
    assert "?" in result
    for pattern in included_patterns:
        assert pattern in result
    for pattern in absent_patterns:
        assert pattern not in result


@pytest.mark.parametrize(
    "field, query, included_patterns, absent_patterns",
    [
        (
            # `field`
            "lorem_ipsum",
            # `query`
            "в",
            # `included_patterns`
            [
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='1'),
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='2'),
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='Lorem Ipsum'),
                'Лорем ипсум',
            ]
        ),
        (
            # `field`
            "lorem_ipsum",
            # `query`
            "разработка",
            # `included_patterns`
            [
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='1'),
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='2'),
                'Lorem Ipsum',
                'Лорем ипсум',
            ]
        ),
    ]
)
def test_tf_idf_query_page(
        test_client: flask.testing.FlaskClient,
        field: str,
        query: str,
        included_patterns: list[str],
        absent_patterns: list[str]
) -> None:
    """Test page with results of search by natural language query."""
    result = test_client.post(f'/{field}/query', data={'query': query}).data.decode('utf-8')
    assert "/" in result
    assert "⌂" in result
    assert "?" in result
    for pattern in included_patterns:
        assert pattern in result
    for pattern in absent_patterns:
        assert pattern not in result


@pytest.mark.parametrize(
    "field, query, included_patterns, absent_patterns",
    [
        (
            # `field`
            "lorem_ipsum",
            # `query`
            "это tags: рыба",
            # `included_patterns`
            [
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='2'),
            ],
            # `absent_patterns`
            [
                'Лорем ипсум',
            ]
        ),
        (
            # `field`
            "lorem_ipsum",
            # `query`
            " tags: ",
            # `included_patterns`
            [
                "<h2>Ничего не найдено</h2>",
                '<p><span style="background-color: #f1ece8"> tags: </span></p>'
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='1'),
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='2'),
                'Lorem Ipsum',
                'Лорем ипсум',
            ]
        ),
        (
            # `field`
            "lorem_ipsum",
            # `query`
            "булки tags: lorem ipsum",
            # `included_patterns`
            [
                "<h2>Запрос не может быть обработан</h2>",
                '<p><span style="background-color: #f1ece8">булки tags: lorem ipsum</span></p>'
            ],
            # `absent_patterns`
            [
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='1'),
                TITLE_TEMPLATE.format(field='lorem_ipsum', title='2'),
                'Lorem Ipsum',
                'Лорем ипсум',
            ]
        ),
    ]
)
def test_combined_query_page(
        test_client: flask.testing.FlaskClient,
        field: str,
        query: str,
        included_patterns: list[str],
        absent_patterns: list[str]
) -> None:
    """Test page with results of combined search."""
    result = test_client.post(f'/{field}/query', data={'query': query}).data.decode('utf-8')
    assert "/" in result
    assert "⌂" in result
    assert "?" in result
    for pattern in included_patterns:
        assert pattern in result
    for pattern in absent_patterns:
        assert pattern not in result
