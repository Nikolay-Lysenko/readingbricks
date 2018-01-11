"""
This is the main Flask script for web version of the project.

@author: Nikolay Lysenko
"""


import os
from flask import Flask, render_template
from flask_misaka import Misaka, markdown


app = Flask(__name__)
markdown_preprocessor = Misaka()
markdown_preprocessor.init_app(app)


@app.route('/notes/<note_name>')
def page_with_note(note_name):
    rel_requested_path = f'markdown_notes/{note_name}.md'
    abs_requested_path = os.path.dirname(__file__) + '/' + rel_requested_path
    if not os.path.isfile(abs_requested_path):
        return page_not_found(note_name)
    with open(abs_requested_path, 'r') as source_file:
        content_in_markdown = ''.join(source_file.read())
    preprocessed_content = markdown_preprocessor.render(
        content_in_markdown,
        math=True, math_explicit=True, no_intra_emphasis=True
    )
    content_in_html = render_template('page_with_note.html', **locals())
    content_in_html = content_in_html.replace('</p>\n\n<ul>', '</p>\n<ul>')
    return content_in_html


@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.html'), 404


app.run(debug=True)
