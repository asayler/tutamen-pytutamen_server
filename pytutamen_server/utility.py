# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import datetime
import uuid

from . import crypto


### Constants ###

AUTHZ_KEY_CLIENTUID = 'clientuid'
AUTHZ_KEY_EXPIRATION = 'expiration'
AUTHZ_KEY_OBJPERM = 'objperm'
AUTHZ_KEY_OBJTYPE = 'objtype'
AUTHZ_KEY_OBJUID = 'objuid'


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

def sign_auth_token(priv_key, clientuid, expiration, objperm, objtype, objuid):
    """Sign and encode assertion token"""

    val = { AUTHZ_KEY_CLIENTUID: str(clientuid),
            AUTHZ_KEY_EXPIRATION: int(expiration.timestamp()),
            AUTHZ_KEY_OBJPERM: str(objperm),
            AUTHZ_KEY_OBJTYPE: str(objtype),
            AUTHZ_KEY_OBJUID: str(objuid)}

    return crypto.sign_jwt(val, priv_key)

def verify_auth_token(pub_key, token):
    """Verify and decode assertion token"""

    out = crypto.verify_jwt(token, pub_key)

    val = { AUTHZ_KEY_CLIENTUID: uuid.UUID(out[AUTHZ_KEY_CLIENTUID]),
            AUTHZ_KEY_EXPIRATION: datetime.datetime.fromtimestamp(int(out[AUTHZ_KEY_EXPIRATION])),
            AUTHZ_KEY_OBJPERM: str(out[AUTHZ_KEY_OBJPERM]),
            AUTHZ_KEY_OBJTYPE: str(out[AUTHZ_KEY_OBJTYPE]),
            AUTHZ_KEY_OBJUID: uuid.UUID(out[AUTHZ_KEY_OBJUID]) }

    return val