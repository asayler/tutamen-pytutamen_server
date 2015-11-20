import sys

# TODO: Make path configurable
sys.path.append('/srv/@public/www/tutamen-server/')

from api.api import app as application
