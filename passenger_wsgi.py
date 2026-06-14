import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app import app

# Passenger strips the sub-path prefix before passing requests to Flask,
# but doesn't set SCRIPT_NAME, so url_for() generates URLs without the
# prefix. This middleware sets SCRIPT_NAME on every request so Flask
# includes the prefix in all generated links.
script_name = os.environ.get('APPLICATION_ROOT', '/')

class PrefixMiddleware:
    def __init__(self, wsgi_app, prefix):
        self.app = wsgi_app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        environ['SCRIPT_NAME'] = self.prefix
        return self.app(environ, start_response)

if script_name and script_name != '/':
    application = PrefixMiddleware(app, script_name)
else:
    application = app
