"""
This script launches Flask application locally.

@author: Nikolay Lysenko
"""


from readingbricks import app
from readingbricks.db_control import DatabaseCreator
from readingbricks.markdown_notes_control import MarkdownDirectoryCreator
from readingbricks.path_configuration import (
    get_path_to_ipynb_notes, get_path_to_markdown_notes, get_path_to_db
)


ipynb_path = get_path_to_ipynb_notes()
markdown_path = get_path_to_markdown_notes()
db_path = get_path_to_db()

md_creator = MarkdownDirectoryCreator(ipynb_path, markdown_path)
md_creator.create_or_update_directory_with_markdown_notes()
db_creator = DatabaseCreator(ipynb_path, db_path)
db_creator.create_or_update_db()

app.run(debug=True)
