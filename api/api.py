#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###
import flask
import flask.ext.httpauth
import flask.ext.cors

### Constants ###


### Global Setup ###

app = flask.Flask(__name__)
app.config['JSON_AS_ASCII'] = False
cors = flask.ext.cors.CORS(app, headers=["Content-Type", "Authorization"])
httpauth = flask.ext.httpauth.HTTPBasicAuth()


### Logging ###


### Functions ###


### Endpoints ###

## Root Endpoints ##

@app.route("/", methods=['GET'])
def get_root():

    app.logger.debug("GET ROOT")
    return app.send_static_file('index.html')


### Exceptions ###

@app.errorhandler(KeyError)
def bad_key(error):
    err = { 'status': 400,
            'message': "{:s}".format(error) }
    app.logger.info("Client Error: KeyError: {:s}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(ValueError)
def bad_value(error):
    err = { 'status': 400,
            'message': "{:s}".format(error) }
    app.logger.info("Client Error: ValueError: {:s}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(TypeError)
def bad_type(error):
    err = { 'status': 400,
            'message': "{:s}".format(error) }
    app.logger.info("Client Error: TypeError: {:s}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(400)
def bad_request(error=False):
    err = { 'status': 400,
            'message': "Malformed request" }
    app.logger.info("Client Error: 400: {:s}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(401)
def not_authorized_401(error=False):
    err = { 'status': 401,
            'message': "Not Authorized" }
    app.logger.info("Client Error: 401: {:s}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(404)
def not_found(error=False):
    err = { 'status': 404,
            'message': "Not Found: {:s}".format(flask.request.url) }
    app.logger.info("Client Error: 404: {:s}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res

@app.errorhandler(405)
def bad_method(error=False):
    err = { 'status': 405,
            'message': "Bad Method: {:s} {:s}".format(flask.request.method, flask.request.url) }
    app.logger.info("Client Error: 405: {:s}".format(err))
    res = flask.jsonify(err)
    res.status_code = err['status']
    return res


### Run Test Server ###

if __name__ == "__main__":
    app.run(debug=True)
