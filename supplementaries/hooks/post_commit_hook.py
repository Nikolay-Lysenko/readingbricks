#!/usr/bin/env python
# Be sure that a copy of this file is placed to `../../../.git/hooks`
# directory under name `post-commit` (without extension).


"""
This script commits the latest versions of automatically managed files.

The script is called after every commit automatically if its copy
is placed and named correctly.

Author: Nikolay Lysenko
"""


import os
import subprocess


def main():
    """
    Add to the current commit files that were added to the next commit.

    Note that these files must be added beforehand by pre-commit hook.
    """
    # Break infinite recursion with disabling post-commit hooks.
    subprocess.run(
        '[ -x {file} ] && chmod -x {file}'.format(file=__file__),
        shell=True
    )

    # Edit current commit.
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
