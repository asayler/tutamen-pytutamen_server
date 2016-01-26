# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2016


### Imports ###

import logging


### Constants ###



### Logging ###

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())


### Authmod ###

class Authmod(object):

    def __init__(self, authenticator, return_val=None):

        # Call Parent
        super().__init__()

        if return_val is None:
            return_val = authenticator.userdata.get('return_val', None)

        if return_val is None:
            return_val = True
        else:
            if (return_val.lower() == 'true'):
                return_val = True
            else:
                return_val = False

        # Save Args
        self._authenticator = authenticator
        self._return_val = return_val

    def run(self, authorization):

        return self._return_val
