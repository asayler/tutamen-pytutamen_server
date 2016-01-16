# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

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
