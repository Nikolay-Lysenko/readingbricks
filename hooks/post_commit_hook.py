#!/usr/bin/env python
# Be sure that a copy of this file is placed to `../.git/hooks` directory
# under name `post-commit` (without extension).


"""
This script adds to the current commit refreshed versions of
automatically managed files.
The script is called after every commit automatically if its copy
is placed and named correctly.

@author: Nikolay Lysenko
"""


import os
import subprocess


def main():
    # Pre-commit hook has added files to the next commit.
    # Add them to the current one.

    # Break infinite recursion with disabling post-commit hooks.
    subprocess.run(
        '[ -x {file} ] && chmod -x {file}'.format(file=__file__),
        shell=True
    )

    relative_path = '../../'
    script_directory = os.path.dirname(__file__)
    absolute_path = os.path.join(script_directory, relative_path)
    subprocess.run(
        'git commit --amend',
        cwd=absolute_path,
        shell=True
    )

    # Enable post-commit hooks again.
    subprocess.run(
        'chmod +x {file}'.format(file=__file__),
        shell=True
    )


if __name__ == '__main__':
    main()
