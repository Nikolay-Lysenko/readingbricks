"""
Just a regular `setup.py` file.

Author: Nikolay Lysenko
"""


import os
from setuptools import setup, find_packages


current_dir = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(current_dir, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='readingbricks',
    version='0.1.0',
    description='Flask app for reading and searching notes from a personal knowledge base',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/Nikolay-Lysenko/readingbricks',
    author='Nikolay Lysenko',
    author_email='nikolay-lysenco@yandex.ru',
    license='MIT',
    keywords='knowledge_base lecture_notes search_engine zettelkasten',
    packages=find_packages(exclude=['git_hooks', 'notes', 'tests']),
    package_data={"readingbricks": ["*.css", "*.html", "*.png"]},
    python_requires='>=3.6',
    install_requires=[
        'Flask',
        'Flask-Markdown',
        'Flask-Misaka',
        'pyparsing',
        'python-markdown-math'
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Education',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Education',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3'
    ]
)
