[![Build Status](https://github.com/Nikolay-Lysenko/readingbricks/actions/workflows/main.yml/badge.svg)](https://github.com/Nikolay-Lysenko/readingbricks/actions/workflows/main.yml)
[![codecov](https://codecov.io/gh/Nikolay-Lysenko/readingbricks/branch/master/graph/badge.svg)](https://codecov.io/gh/Nikolay-Lysenko/readingbricks)
[![Maintainability](https://api.codeclimate.com/v1/badges/ac3959677909d81cb271/maintainability)](https://codeclimate.com/github/Nikolay-Lysenko/readingbricks/maintainability)

# ReadingBricks

## What is it?

It is a structured collection of tagged notes about machine learning theory and practice (now, in Russian only). Each note is independent of the others, but some of them require familiarity with core concepts and definitions.

Two key parts of the repository are as follows:
* The notes itself, all of them are written specially for this project;
* Search system.

Currently, there is a small number of notes and so there is no need in complicated search system. However, an outline of its evolution is created. Planned features of the search system are as follows:
- [x] Search by single tag
- [x] Logical operators
- [ ] Support of tags hierarchy
- [ ] Full-text search
- [ ] Ranking based on flexible parameters
- [ ] On-demand making of customized texts from notes 

## How to use it?

The search system has Flask-based interface. To use this interface, you need to clone the repository to your local machine and install `readingbricks` package. For example, you can do so by running these commands from a terminal:
```
cd /your/path/
git clone https://github.com/Nikolay-Lysenko/readingbricks
cd readingbricks
make venv
```

Every time you want to start a Flask application, do the following:
```
cd /your/path/readingbricks
source venv/bin/activate
python run_app_locally.py
```

The last command launches a local server. After it is ready, open your web browser and go to `127.0.0.1:5000`.

The web interface is quite self-explanatory. There are two elements at the index page:
* search bar,
* cloud of tags.

You can look through the tag cloud and choose the tags you are interested in. If you are interested in a single tag, just push a button with it. However, if you need less trivial selection of notes, search bar should be used. Arbitrary logical expressions with AND, OR, and NOT operators and parentheses are supported there. 

Enjoy reading!

## How to contribute?

Everyone can create a pull request.

Note that it is strongly recommended to update counts of tags automatically. This is easy — just copy and rename files from `supplementaries/hooks` directory according to instructions that are placed inside of them right below shebang. If it is done correctly, Git hooks will refresh tag statistics and other necessary files for you. Also they will validate your notes and check code style.

When working on a pull request, keep in mind internal structure of the project. It is assumed that there are three types of files:
* Notes written by humans. All of them must be inside `notes` directory in `ipynb` format;
* Automatically created files. They never should be updated manually and most of them are in `.gitignore`;
* Infrastructure code. It can be stored at these locations:
    - `readingbricks` (Flask-based interface),
    - `supplementaries/hooks` (Git hooks),
    - `tests` (tests for continuous integration).
