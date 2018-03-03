"""
Just a regular `setup.py` file.

@author: Nikolay Lysenko
"""


import os
from setuptools import setup, find_packages


current_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(current_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='readingbricks',
    version='0.1a',
    description='Flask app for searching through tagged notes in ipynb cells',
    long_description=long_description,
    url='https://github.com/Nikolay-Lysenko/readingbricks',
    author='Nikolay Lysenko',
    author_email='nikolay-lysenco@yandex.ru',
    license='MIT',
    keywords='machine_learning lecture_notes search_engine',
    packages=find_packages(exclude=['notes', 'tests', 'supplementaries']),
    include_package_data=True,  # For CSS files and so on.
    python_requires='>=3.6',
    install_requires=['Flask', 'Flask-Markdown', 'Flask-Misaka']
)
