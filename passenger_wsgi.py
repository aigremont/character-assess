import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))

# Tell Flask the sub-path prefix so url_for() generates correct links.
# Passenger strips the prefix before passing requests to us, so Flask
# just needs to know to include it when building URLs.
script_name = os.environ.get('APPLICATION_ROOT', '/')
if script_name != '/':
    os.environ['SCRIPT_NAME'] = script_name

from app import app as application
