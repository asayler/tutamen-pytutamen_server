# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###


### API Exceptions ###

def APIError(Exception):
    pass

def SSLError(APIError):
    pass

def SSLClientCertError(SSLError):
    pass
