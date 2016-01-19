# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import datetime
import uuid
import logging
import threading

import jwt
import requests

from . import crypto


### Constants ###

AUTHZ_KEY_CLIENTUID = 'clientuid'
AUTHZ_KEY_EXPIRATION = 'expiration'
AUTHZ_KEY_OBJPERM = 'objperm'
AUTHZ_KEY_OBJTYPE = 'objtype'
AUTHZ_KEY_OBJUID = 'objuid'


### Logging ###

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())


### Helper Functions ###

def check_isinstance(obj, *classes):

    for cls in classes:
        if isinstance(obj, cls):
            return

    msg = "'{}' is not an instance of '{}'".format(type(obj), classes)
    raise TypeError(msg)

def check_issubclass(sub, *supers):

    for sup in supers:
        if issubclass(sub, sup):
            return

    msg = "'{}' is not a subclass of '{}'".format(sub, supers)
    raise TypeError(msg)

def nos(val):
    """ None or Str"""
    return str(val) if val is not None else None


### Authorization Functions ###

def encode_auth_token(priv_key, clientuid, expiration, objperm, objtype, objuid=None):
    """Sign and encode assertion token"""

    val = { AUTHZ_KEY_CLIENTUID: str(clientuid),
            AUTHZ_KEY_EXPIRATION: int(expiration.timestamp()),
            AUTHZ_KEY_OBJPERM: objperm,
            AUTHZ_KEY_OBJTYPE: objtype,
            AUTHZ_KEY_OBJUID: str(objuid) if objuid else "" }

    return crypto.sign_jwt(val, priv_key)

def decode_auth_token(pub_key, token):
    """Verify signiture and decode assertion token"""

    out = crypto.verify_jwt(token, pub_key)

    val = { AUTHZ_KEY_CLIENTUID: uuid.UUID(out[AUTHZ_KEY_CLIENTUID]),
            AUTHZ_KEY_EXPIRATION: datetime.datetime.fromtimestamp(out[AUTHZ_KEY_EXPIRATION]),
            AUTHZ_KEY_OBJPERM: out[AUTHZ_KEY_OBJPERM],
            AUTHZ_KEY_OBJTYPE: out[AUTHZ_KEY_OBJTYPE],
            AUTHZ_KEY_OBJUID: uuid.UUID(out[AUTHZ_KEY_OBJUID]) if out[AUTHZ_KEY_OBJUID] else None }

    return val

def verify_auth_token(token, auth_servers, objperm, objtype, objuid=None, manager=None):

    if not manager:
        manager = SigKeyManager()

    val = None
    for server in auth_servers:
        sigkey = manager.get_sigkey(server)

        try:
            val = decode_auth_token(sigkey, token)
            msg = "Decoded token with server '{}'".format(server)
            logging.debug(msg)
            break
        except jwt.exceptions.DecodeError as err:
            msg = "Failed to decode token with server '{}': {}".format(server, str(err))
            logging.debug(msg)

    if not val:
        msg = "Failed to verify token: No matching servers in '{}'".format(auth_servers)
        logging.warning(msg)
        return None

    # Check ClientID
    # ToDo: May not be necessary - but if desired, it
    #       will require having the client co-sign each
    #       token and send a copy of its client cert -
    #       which will also need to be verifed aginst the
    #       server CA. I.e. It's involved.

    # Check Expiration
    token_expiration = val[AUTHZ_KEY_EXPIRATION]
    if token_expiration < datetime.datetime.now():
        msg = "Failed to verify token: Expired at '{}'".format(token_expiration)
        logging.warning(msg)
        return None

    # Check objperm
    token_objperm = val[AUTHZ_KEY_OBJPERM]
    if token_objperm != objperm:
        msg = "Failed to verify token: Objperm '{}' != '{}'".format(token_objperm, objperm)
        logging.warning(msg)
        return None

    # Check objtype
    token_objtype = val[AUTHZ_KEY_OBJTYPE]
    if token_objtype != objtype:
        msg = "Failed to verify token: Objtype '{}' != '{}'".format(token_objtype, objtype)
        logging.warning(msg)
        return None

    # Check objuid
    token_objuid = val[AUTHZ_KEY_OBJUID]
    if token_objuid != objuid:
        msg = "Failed to verify token: Objuid '{}' != '{}'".format(token_objuid, objuid)
        logging.warning(msg)
        return None

    # Verified!
    return server


### Classes ###

class SigkeyManager(object):


    def __init__(self):

        # Call Parent
        super().__init__()

        self.cache_sem = threading.BoundedSemaphore()
        self.cache = {}

    def url_sigkey(self, url_srv):

        API_BASE = 'api'
        API_VERSION = 'v1'
        EP_PUBLIC = 'public'
        EP_SIGKEY = 'sigkey'

        return "{}/{}/{}/{}/{}/".format(url_srv, API_BASE, API_VERSION, EP_PUBLIC, EP_SIGKEY)

    def get_sigkey(self, url_srv, cache=True):

        KEY_SIGKEY = 'sigkey'

        url_srv = url_srv.rstrip('/')
        if cache:
            with self.cache_sem:
                if url_srv in self.cache:
                    return self.cache[url_srv]

        url = url_sigkey(url_srv)
        res = requests.get(url, verify=True)
        res.raise_for_status()
        res_json = res.json()
        sigkey = res_json[KEY_SIGKEY]

        if cache:
            with self.cache_sem:
                self.cache[url_srv] = sigkey

        return sigkey
