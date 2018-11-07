"""
This is the script that initializes Flask app.

Author: Nikolay Lysenko
"""


from flask import Flask

from readingbricks import settings


app = Flask(__name__)
app.config['path_to_ipynb_notes'] = settings.get_path_to_ipynb_notes()
app.config['path_to_markdown_notes'] = settings.get_path_to_markdown_notes()
app.config['path_to_db'] = settings.get_path_to_db()
app.config['path_to_counts_of_tags'] = settings.get_path_to_counts_of_tags()


# Flask requires to import `views` after `app` is set
# in order to decorate views and register routes.
# Thus, E402 and F401 style violations should be ignored here.
import readingbricks.views  # noqa: E402, F401
