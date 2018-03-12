"""
Tests of functions that render HTML pages.

@author: Nikolay Lysenko
"""


import unittest
import os

from readingbricks import app
from readingbricks.db_control import DatabaseCreator
from readingbricks.markdown_notes_control import MarkdownDirectoryCreator


class TestViews(unittest.TestCase):
    """
    Tests of functions for rendering pages in HTML.
    """

    @staticmethod
    def setUpClass():
        # Do preparations that must be done once before all tests.
        app.testing = True

        dir_path = os.path.dirname(__file__)
        ipynb_path = os.path.join(dir_path, 'resources/sample_notebooks')
        markdown_path = os.path.join(dir_path, 'markdown_notes')
        db_path = os.path.join(dir_path, 'tag_to_notes.db')
        counts_path = os.path.join(dir_path, 'resources/counts_of_tags.tsv')

        md_creator = MarkdownDirectoryCreator(ipynb_path, markdown_path)
        md_creator.create_or_update_directory_with_markdown_notes()
        db_creator = DatabaseCreator(ipynb_path, db_path)
        db_creator.create_or_update_db()

        app.config['path_to_ipynb_notes'] = ipynb_path
        app.config['path_to_markdown_notes'] = markdown_path
        app.config['path_to_db'] = db_path
        app.config['path_to_counts_of_tags'] = counts_path

    def setUp(self):
        # Do preparations that must be done before each test.
        self.app = app.test_client()

    def test_index(self):
        """
        Test index page.

        :return:
            None
        """
        result = str(self.app.get('/').data)
        self.assertTrue('letters (4)' in result)
        self.assertTrue('digits (2)' in result)


def main():
    test_loader = unittest.TestLoader()
    suites_list = []
    testers = [
        TestViews()
    ]
    for tester in testers:
        suite = test_loader.loadTestsFromModule(tester)
        suites_list.append(suite)
    overall_suite = unittest.TestSuite(suites_list)
    unittest.TextTestRunner().run(overall_suite)


if __name__ == '__main__':
    main()
