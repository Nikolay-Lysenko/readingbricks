# Reading Bricks

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

There are two main interfaces that allow browsing notes efficiently:
* Jupyter-based (now it is the recommended way, but it will be deprecated in the future),
* Flask-based (it will be the recommended way in the future).

#### Jupyter-based interface

When the repository is cloned to your local machine, open the file named `supplementaries/counts_of_tags.tsv`. It contains tags and their frequencies in tab-separated format. Look through the file and choose the tags you are interested in. Suppose that they are 'tag1', 'tag2', and 'tag3'. To make a notebook with notes that are associated with at least one of these tags, run:
```
python supplementaries/search_in_jupyter_notes.py -e tag1 OR tag2 OR tag3
```

More complex filtering is supported too. You can write arbitrary logical expressions with AND and OR operators and parentheses:
```
python supplementaries/search_in_jupyter_notes.py -e \(tag1 OR tag2\) AND \(tag3 OR tag4\)
```
Do not forget to escape parentheses, because without escaping `bash` fails.

After your query is run, look at the freshly created file named `notes_for_the_last_query.ipynb`. Enjoy reading!

#### Flask-based interface

To use this interface, you need to create a virtual environment (or `conda` environment) with Python 3.6 and packages listed in `requirements.txt`. Activate this environment and run the following command:
```
python run_flask_app.py
```

After local server is started, open your web browser and go to `127.0.0.1:5000`. The web interface is quite self-explanatory. Again, enjoy reading!

## How to contribute?

Everyone can create a pull request.

Note that it is strongly recommended to update counts of tags automatically. This is easy — just copy and rename files from `supplementaries/hooks` directory according to instructions that are placed inside of them right below shebang. If it is done correctly, Git hooks will refresh tag statistics and other necessary files for you. Also they will validate your notes.

When working on a pull request, keep in mind internal structure of the project. It is assumed that there are three types of files:
* Notes written by humans. All of them must be inside `notes` directory in `ipynb` format;
* Automatically created files. They never should be updated manually and most of them are in `.gitignore`;
* Infrastructure code. It can be stored at these locations:
    - `readingbricks` (Flask-based interface),
    - `supplementaries/hooks` (Git hooks),
    - `supplementaries/search_in_jupyter_notes.py` (the only file for Jupyter-based interface).
