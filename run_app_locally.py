"""
Launch Flask application locally.

Author: Nikolay Lysenko
"""


from readingbricks import app
from readingbricks.constants import NOTES_DIR, RESOURCES_DIR
from readingbricks.resources import make_resources


make_resources(NOTES_DIR, RESOURCES_DIR)
app.run(debug=True)
