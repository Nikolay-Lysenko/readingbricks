"""
This script launches Flask application locally.

Author: Nikolay Lysenko
"""


from readingbricks import app
from readingbricks.resources import provide_resources


provide_resources()
app.run(debug=True)
