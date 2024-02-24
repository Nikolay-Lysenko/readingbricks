"""
Store default settings.

Author: Nikolay Lysenko
"""


import os

# Below variables are uploaded to app config, so there are no unused imports.
from readingbricks.constants import (  # noqa: F401
    MARKDOWN_DIR_NAME,
    TAG_COUNTS_FILE_NAME,
    TAG_TO_NOTES_DB_FILE_NAME,
    TF_IDF_DB_FILE_NAME
)


LANGUAGE = 'ru'

FIELDS = [
    "machine_learning",
]
FIELD_TO_ALIAS = {
    "machine_learning": "Машинное обучение",
}
FIELD_TO_SEARCH_PROMPT = {
    "machine_learning": "трансформер tags: естественные_языки OR рекомендательные_системы",
}

NOTES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "notes"))
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")
