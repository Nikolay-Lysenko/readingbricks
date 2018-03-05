"""
Tests of functions that are executed before every start of Flask app.

@author: Nikolay Lysenko
"""


import unittest

from readingbricks.ipynb_utils import extract_cells


class TestJupyterCellsExtraction(unittest.TestCase):
    """
    Tests of tools for iterating over Jupyter cells.
    """

    def test_extract_cells(self):
        """
        Test `extract_cells` function.

        :return:
             None
        """
        # Path is taken relatively `readingbricks` directory for `pytest`.
        path = 'tests/resources_for_tests/sample_notebooks'
        result = list(extract_cells(path))
        letters_content = sorted(
            [
                cell['source']
                for cell in result
                if 'letters' in cell['metadata']['tags']
            ]
        )
        true_letters_content = [
            ['## A\n', '\n', 'A'],
            ['## B\n', '\n', 'B'],
            ['## C\n', '\n', 'C'],
            ['## D\n', '\n', 'D']
        ]
        self.assertEqual(letters_content, true_letters_content)
        digits_content = sorted(
            [
                cell['source']
                for cell in result
                if 'digits' in cell['metadata']['tags']
            ]
        )
        true_digits_content = [
            ['## 1\n', '\n', '1'],
            ['## 2\n', '\n', '2']
        ]
        self.assertEqual(digits_content, true_digits_content)


def main():
    test_loader = unittest.TestLoader()
    suites_list = []
    testers = [
        TestJupyterCellsExtraction()
    ]
    for tester in testers:
        suite = test_loader.loadTestsFromModule(tester)
        suites_list.append(suite)
    overall_suite = unittest.TestSuite(suites_list)
    unittest.TextTestRunner().run(overall_suite)


if __name__ == '__main__':
    main()
