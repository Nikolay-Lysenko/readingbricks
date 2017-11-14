# Snip & Ship

## What is ?

It is a structured collection of tagged snippets about machine learning theory and practice (now, in Russian only).

Two key parts of the repository are as follows:
* Snippets itself,
* Search system.

Currently, there is a small number of snippets and so there is no need in complicated search system. However, an outline of its evolution is created. Planned features of the search system are as follows:
- [x] Search by tags
- [ ] Logical operators
- [ ] Support of tags hierarchy
- [ ] Full-text search
- [ ] Ranking based on flexible parameters

## How to use it?

As always, this repository can be cloned to your local machine. Just run `git clone https://github.com/Nikolay-Lysenko/snip_and_ship` from your terminal.

When repository is cloned, find interesting tags in the file named `list_of_tags.txt`. Suppose that they are 'tag1', 'tag2', and 'tag3'. To make a notebook with snippets that are associated with at least one of these tags, run:

```
python search.py -t tag1 tag2 tag3
```

Go to `snippets` directory and look at the freshly created file named `snippets_that_match_query.ipynb`. Enjoy reading!

## How to contribute?

Everyone can create a pull request.

Note that it is strongly recommended to update list of tags automatically. This is easy — just copy and rename files from `hooks` directory according to instructions that are placed inside of them right below shebang. If it is done correctly, Git hooks will refresh list of tags for you.


