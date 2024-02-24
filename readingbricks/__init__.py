"""
Initialize and configure Flask app.

Author: Nikolay Lysenko
"""


from flask import Flask

from readingbricks import default_settings


app = Flask(__name__)
app.config.from_object(default_settings)


# Flask requires to import `views` after `app` is set
# in order to decorate views and register routes.
# Thus, E402 and F401 style violations should be ignored here.
import readingbricks.views  # noqa: E402, F401
