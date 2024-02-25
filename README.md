[![Build Status](https://github.com/Nikolay-Lysenko/readingbricks/actions/workflows/main.yml/badge.svg)](https://github.com/Nikolay-Lysenko/readingbricks/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/Nikolay-Lysenko/readingbricks/branch/master/graph/badge.svg)](https://codecov.io/gh/Nikolay-Lysenko/readingbricks)
[![Maintainability](https://api.codeclimate.com/v1/badges/ac3959677909d81cb271/maintainability)](https://codeclimate.com/github/Nikolay-Lysenko/readingbricks/maintainability)
[![PyPI version](https://badge.fury.io/py/readingbricks.svg)](https://pypi.org/project/readingbricks/)

# ReadingBricks

## Overview

It is a Flask app for reading and searching notes from a personal knowledge base. Here, knowledge base means a collection of Jupyter notebooks with Markdown cells which may have tags and may contain links to each other. So, the approach resembles [Zettelkasten](https://en.wikipedia.org/wiki/Zettelkasten).

Features of the search system include:
- [x] Separate spaces for fields of knowledge
- [x] Search by single tag
- [x] Search by expressions consisting of tags, logical operators, and parentheses
- [x] Full-text search with TF-IDF
- [ ] Search within kNN-index built on vector representations of notes

The repository can be used either as a whole (with notes written by me) or as a Python package providing an interface to your notes.

## Usage as existing knowledge base

The most valuable part of this project is not a software. It is the [notes](https://github.com/Nikolay-Lysenko/readingbricks/tree/master/notes) itself. When writing them, I try to explain complicated things in a way that allows efficient grasping with as less ambiguity as possible. I write mostly on machine learning, but new topics are coming. Alas, there is a potential dealbreaker — as of now, the notes are in Russian only. If it does not suit you, please go to the [next section](#usage-as-an-interface).

To start with, you need to clone the repository to your local machine and install `readingbricks` package. This can be done by running the below commands from a terminal:
```bash
cd /your/path/
git clone https://github.com/Nikolay-Lysenko/readingbricks
cd readingbricks
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

Every time you want to start a Flask application, run these commands:
```bash
cd /your/path/readingbricks
source venv/bin/activate
python -m readingbricks
```

The last command launches a local server. After it is ready, open your web browser and go to `127.0.0.1:5000`. See [interface guide](#interface-guide) for further details.

## Usage as an interface

To make your own knowledge base compatible with the app, it must be represented as follows:
```
notes_directory
├── field_one
│   ├── notebook_one.ipynb
│   ├── ...
│   └── notebook_n.ipynb
├── ...
└── field_k
    ├── notebook_one.ipynb
    ├── ...
    └── notebook_m.ipynb
```
Here, fields stand for independent domains (say, machine learning, chemistry, music theory, etc.). Within a particular field, distribution of notes among Jupyter notebooks can be arbitrary. For example, you may simply keep all notes in a single notebook.

All cells of a notebook must be Markdown cells starting with `## {title}`. To tag a note, activate tagging facilities with 'View -> Cell Toolbar -> Tags'. To add link from one note to an other note, special patterns `__root_url__/{field}/notes/{note_title}` and `__home_url__/notes/{note_title}` can be used. While the latter is less verbose, only the former supports cross-field links.

So far so good. The knowledge base is ready, but the app must be configured to use it. Create somewhere a JSON file that looks like this:
```json
{
  "LANGUAGE": "en",
  "FIELDS": ["field_one", "field_two"],
  "FIELD_TO_ALIAS": {"field_one": "Field #1", "field_two": "Field #2"},
  "FIELD_TO_SEARCH_PROMPT": {"field_one": "the_most_popular_tag", "field_two": "the_most_popular_tag"},
  "NOTES_DIR": "/absolute/path/to/notes_directory",
  "RESOURCES_DIR": "/any/directory/for/storing/internal/files"
}
```

Now, let us install the Python package:
```bash
source /your/path/venv/bin/activate
pip install readingbricks
```

All that remains is to launch the app:
```bash
python -m readingbricks -c /absolute/path/to/config.json
```

As in the previous section, go to `127.0.0.1:5000`. Known bug is that some minor interface elements are in Russian regardless of notes language. I am still seeking an elegant and maintainable solution to this problem.

## Interface guide

The web interface is quite self-explanatory.

The only non-trivial control element is search bar which is located at home pages of fields. It can operate in three modes:
* query in natural language (e.g., `transformers in recommender systems`);
* query as expression consisting of tags, logical operators, and parentheses — special keyword `tags:` is required (e.g. `tags: transformers AND recommender_systems`);
* combination of above options — symbols before `tags:` form natural language query and symbols after it form tag expression (e.g., `transformers tags: recommender_systems`).

If at least part of a query is in natural language, results are sorted by TF-IDF. Else, order of results depends on lexicographic positions of their notebooks inside their field directory and on positions of cells inside notebooks.

Enjoy reading!
