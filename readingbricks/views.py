"""
Render web pages for Flask application.

Author: Nikolay Lysenko
"""


import os
import sqlite3
import contextlib
from functools import reduce
from typing import Optional, Union

from flask import render_template, url_for, request
from flask_misaka import Misaka
from markupsafe import Markup

from readingbricks import app
from readingbricks.user_query_processing import LogicalQueriesHandler
from readingbricks.utils import compress


RESPONSE_TYPE = Union[str, tuple[str, int]]  # Rendered page and, optionally, status code.


markdown_preprocessor = Misaka()
markdown_preprocessor.init_app(app)


@app.route('/')
def index() -> RESPONSE_TYPE:
    """Render home page."""
    home_url = url_for('index', _external=True)
    links_to_fields = []
    for field_name in app.config['FIELDS']:
        field_alias = app.config['FIELD_TO_ALIAS'].get(field_name, field_name)
        link = f'<a href={home_url}{field_name} class="button">{field_alias}</a>'
        link = f'<div>{link}</div>\n'
        links_to_fields.append(link)
    fields_cloud = Markup(''.join(links_to_fields))
    contents_with_css = render_template('index.html', **locals())
    return contents_with_css


@app.route('/about')
def about() -> RESPONSE_TYPE:
    """Render page with info about the project."""
    return render_template('about.html')


@app.route('/<field_name>')
def field(field_name: str) -> RESPONSE_TYPE:
    """Render page of a particular field."""
    if field_name not in app.config['FIELDS']:
        return render_template('404.html'), 404
    field_alias = app.config['FIELD_TO_ALIAS'].get(field_name, field_name)
    search_prompt = app.config['FIELD_TO_SEARCH_PROMPT'].get(field_name, "")

    tags_with_counts = []
    path_to_tag_counts = os.path.join(
        app.config.get("RESOURCES_DIR"), field_name, app.config.get("TAG_COUNTS_FILE_NAME")
    )
    with open(path_to_tag_counts) as source_file:
        for line in source_file:  # pragma: no branch
            tags_with_counts.append(line.split('\t'))
    home_url = url_for('index', _external=True)
    link_names = [f'{tag} ({count.strip()})' for (tag, count) in tags_with_counts]
    links_to_tags = [
        f'<a href={home_url}{field_name}/tags/{tag} class="button">{name}</a>\n'
        for (tag, counts), name in zip(tags_with_counts, link_names)
    ]
    tags_cloud = Markup(''.join(links_to_tags))

    contents_with_css = render_template('field.html', **locals())
    return contents_with_css


def make_link_from_title(md_title: str, field_name: str) -> str:
    """
    Convert Markdown title to Markdown title with link.

    The process can be illustrated in the following way:
    '## Title' -> '## [Title](URL)'

    As a result, it becomes possible to get permalink to a note found in search results.
    """
    note_title = md_title.lstrip('# ').rstrip('\n')
    home_url = url_for('index', _external=True)
    result = '## ' + f'[{note_title}]({home_url}{field_name}/notes/{note_title})\n'
    return result


def activate_cross_links(contents_in_markdown: str, field_name: str) -> str:
    """
    Make links to other notes valid.

    Substring '__root_url__' is reserved for link to the index page,
    substring '__home_url__' is reserved for link to the field home page,
    and here these substrings are replaced with actual URLs.
    """
    root_url = url_for('index', _external=True)
    contents_in_markdown = contents_in_markdown.replace('__root_url__', root_url)
    home_url = url_for('index', _external=True) + field_name
    contents_in_markdown = contents_in_markdown.replace('__home_url__', home_url)
    return contents_in_markdown


def convert_note_from_markdown_to_html(field_name: str, note_id: str) -> Optional[Markup]:
    """
    Convert a Markdown file into `Markup` instance with HTML inside.

    If requested note does not exist, return `None`.
    """
    dir_path = os.path.join(
        app.config.get("RESOURCES_DIR"), field_name, app.config.get("MARKDOWN_DIR_NAME")
    )
    abs_requested_path = os.path.join(dir_path, f'{note_id}.md')
    if not os.path.isfile(abs_requested_path):
        return None
    with open(abs_requested_path, 'r') as source_file:
        md_title = source_file.readline()
        md_title_as_link = make_link_from_title(md_title, field_name)
        contents_in_markdown = md_title_as_link + source_file.read()
    contents_in_markdown = activate_cross_links(contents_in_markdown, field_name)
    contents_in_html = markdown_preprocessor.render(
        contents_in_markdown,
        math=True, math_explicit=True, no_intra_emphasis=True
    )
    return contents_in_html


@app.route('/<field_name>/notes/<note_title>')
def page_with_note(field_name: str, note_title: str) -> RESPONSE_TYPE:
    """Render in HTML a page with exactly one note."""
    field_url = url_for('field', field_name=field_name)
    note_id = compress(note_title)
    contents_in_html = convert_note_from_markdown_to_html(field_name, note_id)
    if contents_in_html is None:
        return render_template('404.html'), 404
    page_title = note_title
    contents_with_css = render_template('regular_page.html', **locals())
    contents_with_css = contents_with_css.replace('</p>\n\n<ul>', '</p>\n<ul>')
    return contents_with_css


def page_for_list_of_ids(field_name: str, page_title: str, note_ids: list[str]) -> RESPONSE_TYPE:
    """Render in HTML a page with all notes from the specified list."""
    field_url = url_for('field', field_name=field_name)
    notes_contents = []
    for note_id in note_ids:
        notes_contents.append(convert_note_from_markdown_to_html(field_name, note_id))
    contents_in_html = reduce(lambda x, y: x + y, notes_contents)

    if len(note_ids) > 1:
        table_of_contents = ''
        for note_content in notes_contents:
            table_of_contents += note_content.split('\n')[0].replace('h2', 'p') + '\n'

    contents_with_css = render_template('regular_page.html', **locals())
    contents_with_css = contents_with_css.replace('</p>\n\n<ul>', '</p>\n<ul>')
    return contents_with_css


@app.route('/<field_name>/tags/<tag>')
def page_for_tag(field_name: str, tag: str) -> RESPONSE_TYPE:
    """Render in HTML a page with all notes that have the specified tag."""
    path_to_db = os.path.join(
        app.config.get("RESOURCES_DIR"), field_name, app.config.get("TAG_TO_NOTES_DB_FILE_NAME")
    )
    try:
        with contextlib.closing(sqlite3.connect(path_to_db)) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT note_id FROM {tag}")
                query_result = cursor.fetchall()
        note_ids = [x[0] for x in query_result]
    except sqlite3.OperationalError:
        return render_template('404.html'), 404
    page_title = (tag[0].upper() + tag[1:]).replace('_', ' ')
    contents_with_css = page_for_list_of_ids(field_name, page_title, note_ids)
    return contents_with_css


@app.route('/<field_name>/query', methods=['POST'])
def page_for_query(field_name: str) -> RESPONSE_TYPE:
    """
    Render in HTML a page with all notes that match user query.

    A query may contain AND, OR, and NOT operators.
    """
    field_url = url_for('field', field_name=field_name)

    user_query = request.form['query']
    default = app.config['FIELD_TO_SEARCH_PROMPT'].get(field_name, "tag")
    user_query = user_query or default

    path_to_db = os.path.join(
        app.config.get("RESOURCES_DIR"), field_name, app.config.get("TAG_TO_NOTES_DB_FILE_NAME")
    )
    query_handler = LogicalQueriesHandler(path_to_db)
    try:
        note_ids = query_handler.find_all_relevant_notes(user_query)
    except sqlite3.OperationalError:
        return render_template('invalid_query.html', **locals())

    if len(note_ids) > 0:
        contents_with_css = page_for_list_of_ids(field_name, user_query, note_ids)
    else:
        contents_with_css = render_template('empty_result.html', **locals())
    return contents_with_css


@app.errorhandler(404)
def page_not_found(_) -> RESPONSE_TYPE:
    """Render template for unknown page."""
    return render_template('404.html'), 404
