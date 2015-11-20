#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###
import flask
import flask.ext.httpauth
import flask.ext.cors

from . import exceptions

### Constants ###


### Global Setup ###

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cors = flask.ext.cors.CORS(app, headers=["Content-Type", "Authorization"])
httpauth = flask.ext.httpauth.HTTPBasicAuth()

app.debug=True

### Logging ###

if not app.testing:

    import logging
    import logging.handlers

    loggers = [app.logger, logging.getLogger('tutamen')]

    formatter_line = logging.Formatter('%(levelname)s: %(module)s - %(message)s')
    formatter_line_time = logging.Formatter('%(asctime)s %(levelname)s: %(module)s - %(message)s')

    # Stream Handler
    handler_stream = logging.StreamHandler()
    handler_stream.setFormatter(formatter_line)
    if app.debug:
        handler_stream.setLevel(logging.DEBUG)
    else:
        handler_stream.setLevel(logging.INFO)

    # File Handler
    # if not os.path.exists(_LOGGING_PATH):
    #     os.makedirs(_LOGGING_PATH)
    # logfile_path = "{:s}/{:s}".format(_LOGGING_PATH, "api.log")
    # handler_file = logging.handlers.WatchedFileHandler(logfile_path)
    # handler_file.setFormatter(formatter_line_time)
    # if app.debug:
    #     handler_file.setLevel(logging.DEBUG)
    # else:
    #     handler_file.setLevel(logging.INFO)

    for logger in loggers:
        if app.debug:
            logger.setLevel(logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
        logger.addHandler(handler_stream)
    #    logger.addHandler(handler_file)


### Functions ###



### Auth Decorators ###

def authenticate_client():

    def _decorator(func):

        @functools.wraps(func)
        def _wrapper(*args, **kwargs):

            cert_info = flask.request.environ
            status = cert_info['SSL_CLIENT_VERIFY']
            if status != 'SUCCESS':
                msg = "Could not verify client cert: {}".format(status)
                app.logger.error(msg)
                raise exceptions.SSLClientCertError(msg)

            account_id = cert_info['SSL_CLIENT_S_DN_O']
            client_id = cert_info['SSL_CLIENT_S_DN_CN']
            msg = "Authenticated Client '{}' for Account '{}'".format(client_id, account_id)
            app.logger.info(msg)
            flask.g.account_id = account_id
            flask.g.client_id = client_id

            # Call Function
            return func(*args, **kwargs)

        return _wrapper

    return _decorator


### Endpoints ###

## Root Endpoints ##

@app.route("/", methods=['GET'])
@authenticate_client
def get_root():

    app.logger.debug("GET ROOT")
    return app.send_static_file('index.html')

### Exceptions ###

@app.errorhandler(KeyError)
def bad_key(error):
    err = { 'status': 400,
            'message': "{}".format(error) }
    app.logger.info("Client Error: KeyError: {}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(ValueError)
def bad_value(error):
    err = { 'status': 400,
            'message': "{}".format(error) }
    app.logger.info("Client Error: ValueError: {}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(TypeError)
def bad_type(error):
    err = { 'status': 400,
            'message': "{}".format(error) }
    app.logger.info("Client Error: TypeError: {}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(400)
def bad_request(error=False):
    err = { 'status': 400,
            'message': "Malformed request" }
    app.logger.info("Client Error: 400: {}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(401)
def not_authorized_401(error=False):
    err = { 'status': 401,
            'message': "Not Authorized" }
    app.logger.info("Client Error: 401: {}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(404)
def not_found(error=False):
    err = { 'status': 404,
            'message': "Not Found: {}".format(flask.request.url) }
    app.logger.info("Client Error: 404: {}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(405)
def bad_method(error=False):
    err = { 'status': 405,
            'message': "Bad Method: {} {}".format(flask.request.method, flask.request.url) }
    app.logger.info("Client Error: 405: {}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res


### Run Test Server ###

if __name__ == "__main__":
    app.run(debug=True)
