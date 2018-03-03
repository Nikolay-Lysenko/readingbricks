"""
It is just a small module for work with files in Jupyter format,
i.e., files that have `.ipynb` extension.

@author: Nikolay Lysenko
"""


import os
import json
from typing import Dict, Generator, Any


def extract_cells(path_to_dir: str) -> Generator[Dict[str, Any], None, None]:
    """
    Walk through the specified directory and yield cells of
    Jupyter notebooks from there.
    """
    file_names = [x for x in os.listdir(path_to_dir)
                  if os.path.isfile(os.path.join(path_to_dir, x))]
    for file_name in file_names:
        with open(os.path.join(path_to_dir, file_name)) as source_file:
            cells = json.load(source_file)['cells']
            for cell in cells:
                yield cell
