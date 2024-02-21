"""
Store global constants.

Author: Nikolay Lysenko
"""


import os


FIELDS = [
    "machine_learning",
]
FIELD_TO_ALIAS = {
    "machine_learning": "Машинное обучение",
}
FIELD_TO_SEARCH_PROMPT = {
    "machine_learning": "нейронные_сети AND (байесовские_методы OR методы_оптимизации)",
}

NOTES_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "notes"))
RESOURCES_DIR = os.path.join(os.path.dirname(__file__), "resources")
MARKDOWN_DIR_NAME = "markdown_notes"
TAG_COUNTS_FILE_NAME = "tag_counts.tsv"
TAG_TO_NOTES_DB_FILE_NAME = "tag_to_notes.db"
