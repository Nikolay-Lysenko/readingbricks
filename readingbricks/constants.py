"""
Store global constants.

Author: Nikolay Lysenko
"""


LANGUAGES_FOR_STEMMER = {"en": "english", "ru": "russian"}
MARKDOWN_DIR_NAME = "markdown_notes"
TAG_COUNTS_FILE_NAME = "tag_counts.tsv"
TAG_TO_NOTES_DB_FILE_NAME = "tag_to_notes.db"
TF_IDF_DB_FILE_NAME = "tf_idf.db"

TITLES_BY_TEMPLATE_AND_LANG = {
    "404.html": {"en": "Page not found", "ru": "Страница не найдена"},
    "about.html": {"en": "About", "ru": "О проекте"},
    "empty_result.html": {"en": "Nothing found", "ru": "Ничего не найдено"},
    "index.html": {"en": "Index", "ru": "Главная"},
    "invalid_query.html": {"en": "Check your query", "ru": "Проверьте запрос"},
}
