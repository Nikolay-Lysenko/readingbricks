"""
Connect the Flask app to a web server (for example, `uwsgi`).

Author: Nikolay Lysenko
"""


from readingbricks import app


if __name__ == '__main__':
    app.run()
