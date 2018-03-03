"""
This script launches Flask application locally.

@author: Nikolay Lysenko
"""


from readingbricks import app
from readingbricks.db_control import create_or_refresh_db
from readingbricks.markdown_notes_control import (
    refresh_directory_with_markdown_notes
)


create_or_refresh_db()
refresh_directory_with_markdown_notes()
app.run(debug=True)
