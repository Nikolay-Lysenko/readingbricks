[![Build Status](https://travis-ci.org/Nikolay-Lysenko/readingbricks.svg?branch=master)](https://travis-ci.org/Nikolay-Lysenko/readingbricks)
[![codecov](https://codecov.io/gh/Nikolay-Lysenko/readingbricks/branch/master/graph/badge.svg)](https://codecov.io/gh/Nikolay-Lysenko/readingbricks)
[![Maintainability](https://api.codeclimate.com/v1/badges/ac3959677909d81cb271/maintainability)](https://codeclimate.com/github/Nikolay-Lysenko/readingbricks/maintainability)

# ReadingBricks

## What is it?

It is a structured collection of tagged notes about machine learning theory and practice (now, in Russian only). Each note is independent of the others, but some of them require familiarity with core concepts and definitions.

Two key parts of the repository are as follows:
* The notes itself, all of them are written specially for this project;
* Search system.

Currently, there are a small number of notes and so there is no need in complicated search system. However, an outline of its evolution is created. Planned features of the search system are as follows:
- [x] Search by single tag
- [x] Logical operators
- [ ] Support of tags hierarchy
- [ ] Full-text search
- [ ] Ranking based on flexible parameters
- [ ] On-demand making of customized texts from notes 

## How to use it?

There are two interfaces that allow browsing notes efficiently:
* Flask-based (it is the recommended way),
* Jupyter-based (it will be deprecated in the future; links to other notes are not supported).

#### Flask-based interface

To use this interface, you need to clone the repository to your local machine and install `readingbricks` package. For example, you can do so by running these commands from a terminal:
```
cd /your/path/
git clone https://github.com/Nikolay-Lysenko/readingbricks
cd readingbricks
conda create -n readingbricks_env python=3.6
source activate readingbricks_env
pip install -e .
```

Every time you want to start a Flask application, do the following:
```
source activate readingbricks_env
python /your/path/readingbricks/run_flask_app.py
```

The last command launches a local server. After it is ready, open your web browser and go to `127.0.0.1:5000`.

The web interface is quite self-explanatory. There are two elements at the index page:
* search bar,
* cloud of tags.

You can look through the tag cloud and choose the tags you are interested in. If you are interested in a single tag, just push a button with it. However, if you need less trivial selection of notes, search bar should be used. Arbitrary logical expressions with AND and OR operators and parentheses are supported there. 

Enjoy reading!

#### Jupyter-based interface

If you do not want to use the Flask app, open the file named `supplementaries/counts_of_tags.tsv`. It contains tags and their frequencies in tab-separated format. You can decide what to read based on it. To create a Jupyter notebook with notes that match a query `(tag1 OR tag2) AND (tag3 OR tag4)`, run:
```
cd /your/path/readingbricks/supplementaries
python search_in_jupyter_notes.py -e \(tag1 OR tag2\) AND \(tag3 OR tag4\)
```
Do not forget to escape parentheses, because without escaping `bash` fails.

After your query is run, look at the freshly created file named `notes_for_the_last_query.ipynb`. Again, enjoy reading!

## How to contribute?

Everyone can create a pull request.

Note that it is strongly recommended to update counts of tags automatically. This is easy — just copy and rename files from `supplementaries/hooks` directory according to instructions that are placed inside of them right below shebang. If it is done correctly, Git hooks will refresh tag statistics and other necessary files for you. Also they will validate your notes.

When working on a pull request, keep in mind internal structure of the project. It is assumed that there are three types of files:
* Notes written by humans. All of them must be inside `notes` directory in `ipynb` format;
* Automatically created files. They never should be updated manually and most of them are in `.gitignore`;
* Infrastructure code. It can be stored at these locations:
    - `readingbricks` (Flask-based interface),
    - `supplementaries/hooks` (Git hooks),
    - `supplementaries/search_in_jupyter_notes.py` (the only file for Jupyter-based interface),
    - `tests` (tests for continuous integration).
