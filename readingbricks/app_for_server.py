"""
The script is a connector between the Flask app and a web server.

For example, `uwsgi` can be used as a web server.

Author: Nikolay Lysenko
"""


from readingbricks import app


if __name__ == '__main__':
    app.run()
