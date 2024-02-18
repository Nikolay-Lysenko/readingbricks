"""
Render web pages for Flask application.

Author: Nikolay Lysenko
"""


import os
import sqlite3
import contextlib
from functools import reduce
from typing import List, Tuple, Optional

from flask import render_template, url_for, request
from flask_misaka import Misaka
from markupsafe import Markup

from readingbricks import app
from readingbricks.constants import DOMAINS, DOMAIN_TO_SEARCH_PROMPT, DOMAIN_TO_TRANSLATION
from readingbricks.user_query_processing import LogicalQueriesHandler
from readingbricks.utils import compress


markdown_preprocessor = Misaka()
markdown_preprocessor.init_app(app)


@app.route('/')
def index() -> str:
    """Render home page."""
    home_url = url_for('index', _external=True)
    links_to_domains = []
    for domain_title in DOMAINS:
        translation = DOMAIN_TO_TRANSLATION.get(domain_title, domain_title)
        link = f'<a href={home_url}{domain_title} class="button">{translation}</a>'
        link = f'<div>{link}</div>\n'
        links_to_domains.append(link)
    domains_cloud = Markup(''.join(links_to_domains))
    content_with_css = render_template('index.html', **locals())
    return content_with_css


@app.route('/about')
def about() -> str:
    """Render page with info about the project."""
    return render_template('about.html')


@app.route('/<domain_title>')
def domain(domain_title: str) -> str:
    """Render page of a particular domain."""
    domain_translation = DOMAIN_TO_TRANSLATION.get(domain_title, domain_title)
    search_prompt = DOMAIN_TO_SEARCH_PROMPT.get(domain_title, "")

    tags_with_counts = []
    path_to_tag_counts = app.config.get(domain_title)['path_to_tag_counts']
    with open(path_to_tag_counts) as source_file:
        for line in source_file:  # pragma: no branch
            tags_with_counts.append(line.split('\t'))
    home_url = url_for('index', _external=True)
    link_names = [f'{tag} ({count.strip()})' for (tag, count) in tags_with_counts]
    links_to_tags = [
        f'<a href={home_url}{domain_title}/tags/{tag} class="button">{name}</a>\n'
        for (tag, counts), name in zip(tags_with_counts, link_names)
    ]
    tags_cloud = Markup(''.join(links_to_tags))

    content_with_css = render_template('domain.html', **locals())
    return content_with_css


def make_link_from_title(md_title: str, domain_title: str) -> str:
    """
    Convert Markdown title to Markdown title with link.

    The process can be illustrated in the following way:
    '## Title' -> '## [Title](URL)'
    """
    note_title = md_title.lstrip('# ').rstrip('\n')
    home_url = url_for('index', _external=True)
    result = '## ' + f'[{note_title}]({home_url}{domain_title}/notes/{note_title})\n'
    return result


def activate_cross_links(content_in_markdown: str, domain_title: str) -> str:
    """
    Make links to other notes valid.

    Substring '__home_url__' is reserved for link to the domain home page
    and here this substring is replaced with actual URL.
    """
    home_url = url_for('index', _external=True) + domain_title
    content_in_markdown = content_in_markdown.replace('__home_url__', home_url)
    return content_in_markdown


def convert_note_from_markdown_to_html(domain_title: str, note_id: str) -> Optional[Markup]:
    """
    Convert a Markdown file into `Markup` instance with HTML inside.

    If requested note does not exist, return `None`.
    """
    dir_path = app.config.get(domain_title)['path_to_markdown_notes']
    abs_requested_path = os.path.join(dir_path, f'{note_id}.md')
    if not os.path.isfile(abs_requested_path):
        return None
    with open(abs_requested_path, 'r') as source_file:
        md_title = source_file.readline()
        md_title_as_link = make_link_from_title(md_title, domain_title)
        content_in_markdown = md_title_as_link + source_file.read()
    content_in_markdown = activate_cross_links(content_in_markdown, domain_title)
    content_in_html = markdown_preprocessor.render(
        content_in_markdown,
        math=True, math_explicit=True, no_intra_emphasis=True
    )
    return content_in_html


@app.route('/<domain_title>/notes/<note_title>')
def page_with_note(domain_title: str, note_title: str) -> str:
    """Render in HTML a page with exactly one note."""
    domain_url = url_for('domain', domain_title=domain_title)
    note_id = compress(note_title)
    content_in_html = convert_note_from_markdown_to_html(domain_title, note_id)
    if content_in_html is None:
        return render_template('404.html')
    page_title = note_title
    content_with_css = render_template('regular_page.html', **locals())
    content_with_css = content_with_css.replace('</p>\n\n<ul>', '</p>\n<ul>')
    return content_with_css


def page_for_list_of_ids(domain_title: str, page_title: str, note_ids: List[str]) -> str:
    """Render in HTML a page with all notes from the specified list."""
    domain_url = url_for('domain', domain_title=domain_title)
    notes_content = []
    for note_id in note_ids:
        notes_content.append(convert_note_from_markdown_to_html(domain_title, note_id))
    content_in_html = reduce(lambda x, y: x + y, notes_content)
    content_with_css = render_template('regular_page.html', **locals())
    content_with_css = content_with_css.replace('</p>\n\n<ul>', '</p>\n<ul>')
    return content_with_css


@app.route('/<domain_title>/tags/<tag>')
def page_for_tag(domain_title: str, tag: str) -> str:
    """Render in HTML a page with all notes that have the specified tag."""
    path_to_db = app.config.get(domain_title)['path_to_tag_to_notes_db']
    try:
        with contextlib.closing(sqlite3.connect(path_to_db)) as connection:
            with contextlib.closing(connection.cursor()) as cursor:
                cursor.execute(f"SELECT note_id FROM {tag}")
                query_result = cursor.fetchall()
        note_ids = [x[0] for x in query_result]
    except sqlite3.OperationalError:
        return render_template('404.html')
    page_title = (tag[0].upper() + tag[1:]).replace('_', ' ')
    content_with_css = page_for_list_of_ids(domain_title, page_title, note_ids)
    return content_with_css


@app.route('/<domain_title>/query', methods=['POST'])
def page_for_query(domain_title: str) -> str:
    """
    Render in HTML a page with all notes that match user query.

    A query may contain AND, OR, and NOT operators.
    """
    domain_url = url_for('domain', domain_title=domain_title)

    user_query = request.form['query']
    default = DOMAIN_TO_SEARCH_PROMPT.get(domain_title, "")
    user_query = user_query or default
    if not user_query:
        return render_template('invalid_query.html', **locals())

    path_to_db = app.config.get(domain_title)['path_to_tag_to_notes_db']
    query_handler = LogicalQueriesHandler(path_to_db)
    try:
        note_ids = query_handler.find_all_relevant_notes(user_query)
    except sqlite3.OperationalError:
        return render_template('invalid_query.html', **locals())

    if len(note_ids) > 0:
        content_with_css = page_for_list_of_ids(domain_title, user_query, note_ids)
    else:
        content_with_css = render_template('empty_result.html', **locals())
    return content_with_css


@app.errorhandler(404)
def page_not_found(_) -> Tuple[str, int]:
    """Render template for unknown page."""
    return render_template('404.html'), 404
