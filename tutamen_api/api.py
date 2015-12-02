#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###
import functools

import flask
import flask.ext.httpauth
import flask.ext.cors

from . import exceptions

import pcollections.be_redis_atomic

import tutamen_server.storage


### Constants ###

_REDIS_DB = 3


### Global Setup ###

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cors = flask.ext.cors.CORS(app, headers=["Content-Type", "Authorization"])
httpauth = flask.ext.httpauth.HTTPBasicAuth()


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
    handler_stream.setLevel(logging.DEBUG)

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
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler_stream)
    #    logger.addHandler(handler_file)


### Functions ###

@app.before_request
def before_request():

    driver = pcollections.be_redis_atomic.Driver(db=_REDIS_DB)
    storage = tutamen_server.storage.StorageServer(driver)
    flask.g.srv_storage = storage

@app.teardown_request
def teardown_request(exception):
    pass

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
            app.logger.debug(msg)
            flask.g.account_id = account_id
            flask.g.client_id = client_id

            # Call Function
            return func(*args, **kwargs)

        return _wrapper

    return _decorator


### Endpoints ###

## Root Endpoints ##

@app.route("/", methods=['GET'])
@authenticate_client()
def get_root():

    app.logger.debug("GET ROOT")
    return app.send_static_file('index.html')


## Storage Endpoints ##

@app.route("/secrets/", methods=['POST'])
@authenticate_client()
def post_secret():

    app.logger.debug("POST SECRET")
    d_in = flask.request.get_json(force=True)
    data = d_in['secret']
    sec = flask.g.srv_storage.secret_from_new(data)
    d_out = [sec.uid]
    return flask.jsonify(d_out)

@app.route("/secrets/<uid>/", methods=['GET'])
@authenticate_client()
def get_secret(uid):

    app.logger.debug("GET SECRET")
    sec = flask.g.srv_storage.secret_from_existing(uid)
    d_out = {'secret': sec.data}
    return flask.jsonify(d_out)


### Error Handling ###

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
def not_authorized(error=False):
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
