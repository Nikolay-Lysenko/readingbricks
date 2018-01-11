"""
This is the main Flask script for web version of the project.

@author: Nikolay Lysenko
"""


import os
import sqlite3

from flask import Flask, render_template
from flask_misaka import Misaka, markdown


app = Flask(__name__)
markdown_preprocessor = Misaka()
markdown_preprocessor.init_app(app)


@app.route('/notes/<note_title>')
def page_with_note(note_title):
    """
    Render in HTML a page with exactly one note.
    """
    rel_requested_path = f'markdown_notes/{note_title}.md'
    abs_requested_path = os.path.dirname(__file__) + '/' + rel_requested_path
    if not os.path.isfile(abs_requested_path):
        return page_not_found(note_title)
    with open(abs_requested_path, 'r') as source_file:
        content_in_markdown = ''.join(source_file.read())
    preprocessed_content = markdown_preprocessor.render(
        content_in_markdown,
        math=True, math_explicit=True, no_intra_emphasis=True
    )
    content_in_html = render_template('page_with_note.html', **locals())
    content_in_html = content_in_html.replace('</p>\n\n<ul>', '</p>\n<ul>')
    return content_in_html


@app.route('/tags/<tag>')
def page_for_tag(tag):
    """
    Render in HTML a page with all notes that have the specified tag.
    """
    relative_path_to_db = 'tag_to_notes.db'
    absolute_path_to_db = os.path.dirname(__file__) + '/' + relative_path_to_db
    try:
        conn = sqlite3.connect(absolute_path_to_db)
        cur = conn.cursor()
        cur.execute(f"SELECT note_title FROM {tag}")
        query_result = cur.fetchall()
        note_titles = [x[0] for x in query_result]
    except sqlite3.OperationalError:
        return page_not_found(tag)
    notes_content = []
    for note_title in note_titles:
        notes_content.append(page_with_note(note_title))
    content_in_html = ''.join(notes_content)
    return content_in_html


@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404


app.run(debug=True)
