"""
This is the script that initializes Flask app.

@author: Nikolay Lysenko
"""


from flask import Flask


app = Flask(__name__)
import readingbricks.views  # Flask requires import it after `app` is set.

