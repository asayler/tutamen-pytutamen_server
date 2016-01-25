# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import datetime
import uuid
import logging


### Constants ###


### Logging ###

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())


class AuthenticatorModule(object):

    def __init__(self, authenticator):

        # Call Parent
        super().__init__()

        # Save Args
        self._authenticator = authenticator

    def run(self, authorization):

        return True
