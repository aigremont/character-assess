import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

from app import app
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

app_root = os.environ.get('APPLICATION_ROOT', '/')
if app_root != '/':
    application = DispatcherMiddleware(
        Response('Not Found', status=404),
        {app_root: app}
    )
else:
    application = app
