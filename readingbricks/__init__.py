"""
Initialize Flask app.

Author: Nikolay Lysenko
"""


from flask import Flask

from readingbricks.constants import DOMAINS
from readingbricks.paths import (
    get_path_to_markdown_notes,
    get_path_to_tag_counts,
    get_path_to_tag_to_notes_db
)


app = Flask(__name__)
for domain in DOMAINS:
    app.config[domain] = {
        'path_to_markdown_notes': get_path_to_markdown_notes(domain),
        'path_to_tag_counts': get_path_to_tag_counts(domain),
        'path_to_tag_to_notes_db': get_path_to_tag_to_notes_db(domain)
    }


# Flask requires to import `views` after `app` is set
# in order to decorate views and register routes.
# Thus, E402 and F401 style violations should be ignored here.
import readingbricks.views  # noqa: E402, F401
