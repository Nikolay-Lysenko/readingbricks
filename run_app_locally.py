"""
Launch Flask application locally.

Author: Nikolay Lysenko
"""


from readingbricks import app
from readingbricks.resources import make_resources


make_resources()
app.run(debug=True)
