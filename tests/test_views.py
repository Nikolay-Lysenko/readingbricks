"""
Tests of functions that render HTML pages.

Author: Nikolay Lysenko
"""


import unittest
import os

from readingbricks import app
from readingbricks.resources import provide_resources


class TestViews(unittest.TestCase):
    """Tests of functions for rendering pages in HTML."""

    title_template = (
        '<h2><a href="http://localhost/notes/{title}">{title}</a></h2>'
    )

    @classmethod
    def setUpClass(cls) -> None:
        """Do preparations that must be done once before all tests."""
        app.testing = True

        dir_path = os.path.dirname(__file__)
        ipynb_path = os.path.join(dir_path, 'resources/sample_notebooks')
        markdown_path = os.path.join(dir_path, '.markdown_notes')
        db_path = os.path.join(dir_path, 'tag_to_notes.db')
        counts_path = os.path.join(dir_path, 'resources/counts_of_tags.tsv')

        provide_resources(ipynb_path, markdown_path, db_path)

        app.config['path_to_ipynb_notes'] = ipynb_path
        app.config['path_to_markdown_notes'] = markdown_path
        app.config['path_to_db'] = db_path
        app.config['path_to_counts_of_tags'] = counts_path

    def setUp(self) -> None:
        """Do preparations that must be done before each test."""
        self.app = app.test_client()

    def test_home_page(self) -> None:
        """Test home page."""
        result = self.app.get('/').data.decode('utf-8')
        self.assertTrue('letters (4)' in result)
        self.assertTrue('digits (2)' in result)
        self.assertTrue('list (1)' in result)

    def test_default_page(self) -> None:
        """Test page that is shown when requested page is not found."""
        response = self.app.get('/non_existing')
        result = response.data.decode('utf-8')
        status_code = response.status_code
        self.assertTrue('<title>Страница не найдена</title>' in result)
        self.assertEqual(status_code, 404)

    def test_page_for_note(self) -> None:
        """Test page with a single note."""
        result = self.app.get('/notes/C').data.decode('utf-8')
        self.assertTrue('C:' in result)
        self.assertTrue('<li><p><em>c</em></p></li>' in result)
        self.assertTrue('<li><p>\\(c\\)</p></li>' in result)
        html_link = '<a href="http://localhost/notes/B">link</a>'
        self.assertTrue(html_link in result)
        self.assertFalse(self.title_template.format(title='A') in result)
        result = self.app.get('/notes/non_existing').data.decode('utf-8')
        self.assertTrue('Страница не найдена.' in result)

    def test_page_for_tag(self) -> None:
        """Test page with all notes tagged with a specified tag."""
        result = self.app.get('/tags/digits').data.decode('utf-8')
        self.assertTrue(self.title_template.format(title='1') in result)
        self.assertFalse(self.title_template.format(title='A') in result)

        result = self.app.get('/tags/list').data.decode('utf-8')
        self.assertTrue(self.title_template.format(title='C') in result)
        self.assertFalse(self.title_template.format(title='A') in result)

        result = self.app.get('/tags/non_existing').data.decode('utf-8')
        self.assertTrue('Страница не найдена.' in result)

    def test_page_for_query_with_and(self) -> None:
        """Test search bar requests with AND operator."""
        query = 'list AND letters'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertTrue('C:' in result)
        self.assertTrue('<li><p><em>c</em></p></li>' in result)
        self.assertTrue('<li><p>\\(c\\)</p></li>' in result)
        self.assertFalse(self.title_template.format(title='1') in result)

        query = 'list AND digits'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertTrue('h2>Ничего не найдено</h2>' in result)

    def test_page_for_query_with_or(self) -> None:
        """Test search bar requests with OR operator."""
        query = 'list OR letters'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertTrue(self.title_template.format(title='A') in result)
        self.assertFalse(self.title_template.format(title='1') in result)
        self.assertTrue('<li><p><em>c</em></p></li>' in result)

        query = 'list OR digits'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertFalse(self.title_template.format(title='A') in result)
        self.assertTrue(self.title_template.format(title='1') in result)
        self.assertTrue('<li><p><em>c</em></p></li>' in result)

    def test_page_for_query_with_not(self) -> None:
        """Test search bar requests with NOT operator."""
        query = 'NOT list'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertTrue(self.title_template.format(title='A') in result)
        self.assertFalse(self.title_template.format(title='C') in result)
        self.assertTrue('<p>1</p>' in result)

        query = 'NOT letters'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertFalse(self.title_template.format(title='A') in result)
        self.assertTrue(self.title_template.format(title='1') in result)
        self.assertTrue('<p>2</p>' in result)

    def test_page_for_complex_query(self) -> None:
        """Test search bar requests with NOT, AND, and OR operators."""
        query = '(list AND letters) OR (digits AND letters)'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertTrue(self.title_template.format(title='C') in result)
        self.assertTrue('<li><p><em>c</em></p></li>' in result)
        self.assertFalse(self.title_template.format(title='B') in result)
        self.assertFalse(self.title_template.format(title='1') in result)

        query = '(list AND letters) AND ((digits OR letters OR list) OR list)'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertTrue(self.title_template.format(title='C') in result)
        self.assertTrue('<li><p><em>c</em></p></li>' in result)
        self.assertFalse(self.title_template.format(title='B') in result)
        self.assertFalse(self.title_template.format(title='1') in result)

        query = 'digits OR NOT (letters AND NOT list)'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertTrue(self.title_template.format(title='1') in result)
        self.assertTrue('<li><p><em>c</em></p></li>' in result)
        self.assertFalse(self.title_template.format(title='A') in result)
        self.assertFalse(self.title_template.format(title='D') in result)

        query = '(list AND letters) AND ((digits OR letters OR list) OR lists)'
        response = self.app.post('/query', data={'query': query})
        result = response.data.decode('utf-8')
        self.assertTrue('<h2>Запрос не может быть обработан</h2>' in result)


def main():
    """Run tests."""
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
