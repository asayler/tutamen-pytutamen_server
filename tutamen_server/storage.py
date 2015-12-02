# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as dso
from pcollections import factories as dsf
from pcollections import keys as dsk


### Exceptions ###

class ObjectDNE(Exception):

    def __init__(self, key):

        # Call Parent
        msg = "Object '{:s}' does not exist".format(key)
        super().__init__(msg)



### Objects ###

class StorageServer(object):

    prefix = "storagesrv"
    type_secrets = dso.MutableSet
    key_secrets = "secrets"

    def __init__(self, ds_driver):

        # Call Parent
        super().__init__()

        # Save Attrs
        self._driver = ds_driver

        # Setup Driver-Bound Factories
        self._srv_f_secrets = dsf.InstanceFactory(self._driver, self.type_secrets,
                                                  key_type=dsk.StrKey)
        self._sec_f_data = dsf.InstanceFactory(self._driver, Secret.type_data,
                                               key_type=dsk.UUIDKey,
                                               key_kwargs={'prefix': Secret.prefix,
                                                           'postfix': Secret.postfix_data})

        # Setup Local Collections
        k = "{:s}_{:s}".format(self.prefix, self.key_secrets)
        self._secrets = self._srv_f_secrets.from_raw(k)
        if not self._secrets.exists():
            self._secrets.create(set())

    def wipe(self):
        self._secrets.rem()

    def secret_register(self, secret):
        self._secrets.add(secret.uid)

    def secret_unregister(self, secret):
        self._secrets.discard(secret.uid)

    def secret_exists(self, secret):
        return secret.uid in self._secrets

    def secret_from_new(self, data):
        """New Secret Constructor"""

        uid = uuid.uuid4()
        data = self._sec_f_data.from_new(uid, data)
        sec = Secret(uid, data)
        self.secret_register(sec)
        return sec

    def secret_from_existing(self, uid):
        """Existing Secret Constructor"""

        # Check input
        if not uid in self._secrets:
            raise ObjectDNE(uid)

        uid = uuid.UUID(uid)
        data = self._sec_f_data.from_existing(uid)
        sec = Secret(uid, data)
        return sec

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
