"""
It is just a small module for auxiliary tools.

@author: Nikolay Lysenko
"""


import os
import json
import hashlib
from typing import Dict, Generator, Any


def extract_cells(path_to_dir: str) -> Generator[Dict[str, Any], None, None]:
    """
    Walk through the specified directory and yield cells of
    Jupyter notebooks from there.

    :param path_to_dir:
        path to source directory
    :yield:
        cells as a dictionaries
    """
    file_names = [
        x for x in os.listdir(path_to_dir)
        if os.path.isfile(os.path.join(path_to_dir, x)) and not x.endswith('~')
    ]
    for file_name in file_names:
        with open(os.path.join(path_to_dir, file_name)) as source_file:
            cells = json.load(source_file)['cells']
            for cell in cells:
                yield cell


def compress(string: str, max_length: int = 64) -> str:
    """
    Compress string to a string of restricted length.
    The function can be useful, because some filesystems and/or
    disk encryption impose restriction on maximum length of filename.

    :param string:
        string to be compressed
    :param max_length:
        maximum length of output, default is 64
    :return:
        compressed string
    """
    hashed_string = hashlib.sha256(string.encode('utf-8')).hexdigest()
    result = hashed_string[:max_length]
    return result

