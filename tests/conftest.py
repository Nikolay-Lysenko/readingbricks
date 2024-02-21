"""
Define fixtures.

Author: Nikolay Lysenko
"""


import os
from shutil import rmtree

import flask.testing
import pytest

from readingbricks import app
from readingbricks.resources import make_resources


@pytest.fixture(scope='package', autouse=True)
def resources() -> None:
    """Generate resources for test app."""
    notes_dir = os.path.join(os.path.dirname(__file__), "notes")
    resources_dir = os.path.join(os.path.dirname(__file__), "resources")
    make_resources(notes_dir, resources_dir)
    yield
    rmtree(resources_dir)


@pytest.fixture(scope='module')
def test_client() -> flask.testing.FlaskClient:
    """Provide test client to Flask app."""
    app.testing = True
    app.config["FIELDS"] = ["digits_and_letters", "lorem_ipsum"]
    app.config["FIELD_TO_ALIAS"] = {"digits_and_letters": "Digits & Letters"}
    app.config["FIELD_TO_SEARCH_PROMPT"] = {"digits_and_letters": "digits"}
    app.config["RESOURCES_DIR"] = os.path.join(os.path.dirname(__file__), "resources")
    with app.test_client() as testing_client:
        yield testing_client
