# -*- coding: utf-8 -*-


"""
This module contains web pages for Flask application.

@author: Nikolay Lysenko
"""


import os
import sqlite3
import contextlib
from functools import reduce
from typing import List, Tuple

from flask import render_template, url_for, request
from flask_misaka import Misaka
from markupsafe import Markup

from readingbricks import app
from readingbricks.user_query_processing import LogicalQueriesHandler


markdown_preprocessor = Misaka()
markdown_preprocessor.init_app(app)


@app.route('/')
def index() -> str:
    """
    Render home page.
    """
    lines_in_html = ['<h2>На данный момент доступны следующие метки:</h2>\n']
    tags_with_counts = []
    path_to_counts_of_tags = app.config.get('path_to_counts_of_tags')
    with open(path_to_counts_of_tags) as source_file:
        for line in source_file:
            tags_with_counts.append(line.split('\t'))
    home_url = url_for('index', _external=True)
    link_names = [
        f'{tag} ({count.strip()})' for (tag, count) in tags_with_counts
    ]
    links_to_tags = [
        f'<a href={home_url}tags/{tag} class="button">{name}</a>\n'
        for (tag, counts), name in zip(tags_with_counts, link_names)
    ]
    lines_in_html.extend(links_to_tags)
    tags_cloud = Markup(''.join(lines_in_html))
    content_with_css = render_template('index.html', **locals())
    return content_with_css


def convert_note_from_markdown_to_html(note_title: str) -> Markup:
    """
    Convert note stored as a Markdown file into `Markup` instance
    with HTML inside.
    """
    dir_path = app.config.get('path_to_markdown_notes')
    abs_requested_path = os.path.join(dir_path, f'{note_title}.md')
    if not os.path.isfile(abs_requested_path):
        return render_template('404.html')
    with open(abs_requested_path, 'r') as source_file:
        content_in_markdown = ''.join(source_file.read())
    content_in_html = markdown_preprocessor.render(
        content_in_markdown,
        math=True, math_explicit=True, no_intra_emphasis=True
    )
    return content_in_html


@app.route('/notes/<note_title>')
def page_with_note(note_title: str) -> str:
    """
    Render in HTML a page with exactly one note.
    """
    content_in_html = convert_note_from_markdown_to_html(note_title)
    title = note_title
    content_with_css = render_template('regular_page.html', **locals())
    content_with_css = content_with_css.replace('</p>\n\n<ul>', '</p>\n<ul>')
    return content_with_css


def page_for_list_of_titles(note_titles: List[str], page_title: str) -> str:
    """
    Render in HTML a page with all notes from the specified list.
    """
    notes_content = []
    for note_title in note_titles:
        notes_content.append(convert_note_from_markdown_to_html(note_title))
    content_in_html = reduce(lambda x, y: x + y, notes_content)
    content_with_css = render_template('regular_page.html', **locals())
    content_with_css = content_with_css.replace('</p>\n\n<ul>', '</p>\n<ul>')
    return content_with_css


@app.route('/tags/<tag>')
def page_for_tag(tag: str) -> str:
    """
    Render in HTML a page with all notes that have the specified tag.
    """
    path_to_db = app.config.get('path_to_db')
    try:
        with contextlib.closing(sqlite3.connect(path_to_db)) as conn:
            with contextlib.closing(conn.cursor()) as cur:
                cur.execute(f"SELECT note_title FROM {tag}")
                query_result = cur.fetchall()
        note_titles = [x[0] for x in query_result]
    except sqlite3.OperationalError:
        return render_template('404.html')
    page_title = tag.capitalize().replace('_', ' ')
    content_with_css = page_for_list_of_titles(note_titles, page_title)
    return content_with_css


@app.route('/query', methods=['POST'])
def page_for_query() -> str:
    """
    Render in HTML a page with all notes that match user query
    containing AND and OR operators.
    """
    user_query = request.form['query']
    default = "нейронные_сети AND (постановка_задачи OR байесовские_методы)"
    user_query = user_query or default
    path_to_db = app.config.get('path_to_db')
    query_handler = LogicalQueriesHandler(path_to_db)
    try:
        note_titles = query_handler.find_all_relevant_notes(user_query)
    except sqlite3.OperationalError:
        content_with_css = render_template('invalid_query.html', **locals())
        return content_with_css
    if len(note_titles) > 0:
        content_with_css = page_for_list_of_titles(
            note_titles, page_title=user_query
        )
    else:
        content_with_css = render_template('empty_result.html', **locals())
    return content_with_css


@app.errorhandler(404)
def page_not_found(_) -> Tuple[str, int]:
    return render_template('404.html'), 404
