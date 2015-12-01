# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as dso
from pcollections import factories as dsf
from pcollections import keys as dsk

### Objects ###

class StorageServer(object):

    def __init__(self, ds_driver):

        # Call Parent
        super().__init__()

        # Save Attrs
        self._driver = ds_driver

        # Setup Driver-Bound Factories
        self._sec_f_data = dsf.InstanceFactory(self._driver, Secret.type_data,
                                               key_type=dsk.UUIDKey,
                                               key_kwargs={'prefix': Secret.prefix,
                                                           'postfix': Secret.postfix_data})

    def secret_from_new(self, data):
        """New Secret Constructor"""

        uid = uuid.uuid4()
        data = self._sec_f_data.from_new(uid, data)
        return Secret(uid, data)

    def secret_from_existing(self, uid):
        """Existing Secret Constructor"""

        uid = uuid.UUID(uid)
        data = self._sec_f_data.from_existing(uid)
        return Organization(uid, data)

class Secret(object):

    prefix = "secret"
    type_uid = uuid.UUID
    type_data = dso.String
    postfix_data = "data"

    def __init__(self, uid, data):
        """Initialize Secret"""

        # Call Parent
        super().__init__()

        # Check Args
        if not isinstance(uid, self.type_uid):
            msg = "'uid' must be of type '{}', ".format(self.type_uid)
            msg += "not '{}'".format(type(uid))
            raise TypeError(msg)
        if not isinstance(data, self.type_data):
            msg = "'metadata' must be of type '{}', ".format(self.type_data)
            msg += "not '{}'".format(type(data))
            raise TypeError(msg)

        # Save Attrs
        self._uid = uid
        self._data = data

    @property
    def data(self):
        """Return Secret Data"""
        return str(self._data)

    @property
    def uid(self):
        """Return Secret UUID"""
        return str(self._uid)

    def rem(self):
        """Delete Secret"""
        self._data.rem()
