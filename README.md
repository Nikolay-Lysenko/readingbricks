[![Build Status](https://github.com/Nikolay-Lysenko/readingbricks/actions/workflows/main.yml/badge.svg)](https://github.com/Nikolay-Lysenko/readingbricks/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/Nikolay-Lysenko/readingbricks/branch/master/graph/badge.svg)](https://codecov.io/gh/Nikolay-Lysenko/readingbricks)
[![Maintainability](https://api.codeclimate.com/v1/badges/ac3959677909d81cb271/maintainability)](https://codeclimate.com/github/Nikolay-Lysenko/readingbricks/maintainability)

# ReadingBricks

## Overview

It is a Flask app for reading and searching notes from a personal knowledge base. Here, knowledge base means a collection of Jupyter notebooks with Markdown cells which may have tags and may contain links to each other. So, the approach resembles [Zettelkasten](https://en.wikipedia.org/wiki/Zettelkasten).

Features of the search system include:
- [x] Separate spaces for fields of knowledge
- [x] Search by single tag
- [x] Search by expressions consisting of tags, logical operators, and parenthesis
- [ ] Full-text search with TF-IDF
- [ ] Search within kNN-index built on vector representations of notes

The repository can be used either as a whole (with notes written by me) or as a Python package providing an interface to your notes.

## Usage as existing knowledge base

The most valuable part of this project is not a software. It is the [notes](https://github.com/Nikolay-Lysenko/readingbricks/tree/master/notes) itself. When writing them, I try to explain complicated things in a way that allows efficient grasping with as less ambiguity as possible. I write mostly on machine learning, but new topics are coming. Alas, there is a potential dealbreaker — as of now, notes are in Russian only. If it does not suit you, please go to the next section.

To start with, you need to clone the repository to your local machine and install `readingbricks` package. This can be done by running these commands from a terminal:
```bash
cd /your/path/
git clone https://github.com/Nikolay-Lysenko/readingbricks
cd readingbricks
make venv
```

Every time you want to start a Flask application, run the below commands:
```bash
cd /your/path/readingbricks
source venv/bin/activate
python -m readingbricks
```

The last command launches a local server. After it is ready, open your web browser and go to `127.0.0.1:5000`. See [interface guide](#interface-guide) section for further details.

## Usage as an interface

Coming soon.

## Interface guide

The web interface is quite self-explanatory. At the index page, there is field selection. Home page of each field has two control elements:
* search bar,
* cloud of tags.

You can look through the tag cloud and choose the tags you are interested in. If you are interested in a single tag, just push a button with it. However, if you need less trivial selection of notes, search bar should be used. Arbitrary logical expressions with AND, OR, and NOT operators and parentheses are supported there. 

Enjoy reading!
