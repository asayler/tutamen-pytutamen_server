# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as dso
from pcollections import factories as dsf
from pcollections import keys as dsk

from . import datatypes


### Constants ###

_SERVER_PREFIX = "storagesrv"
_INDEX_KEY_SECRETS = "secrets"


### Exceptions ###



### Objects ###

class StorageServer(datatypes.PersistentObjectServer):

    def __init__(self, driver):

        # Call Parent
        super().__init__(driver)

        # Setup Server Indexes
        idx_key = _SERVER_PREFIX + _INDEX_KEY_SECRETS
        self._index_secrets = datatypes.Index(self, idx_key)
        idx_key = _SERVER_PREFIX + _INDEX_KEY_COLLECTIONS
        self._index_collections = datatypes.Index(self, idx_key)

    def destroy(self):
        self._index_secrets.destroy()
        self._index_collections.destroy()

    def secret_from_new(self, data):
        """New Secret Constructor"""

        uid = uuid.uuid4()
        data = self._sec_f_data.from_new(uid, data)
        sec = Secret(self, uid, data)
        sec.register(_index_secrets)
        return sec

    def secret_from_existing(self, uid):
        """Existing Secret Constructor"""

        # Check input
        if not uid in self._index_secrets.members():
            raise datatypes.ObjectDNE(uid)

        uid = uuid.UUID(uid)
        data = self._sec_f_data.from_existing(uid)
        sec = Secret(self, uid, data)
        return sec

class Secret(datatypes.PersistentObject, datatypes.Indexed):

    def __init__(self, srv, uid, data, metadata):
        """Initialize Secret"""

        # Call Parent
        super().__init__()

        # Check Args
        if not isinstance(srv, StorageServer):
            msg = "'srv' must be of type '{}', ".format(StorageServer)
            msg += "not '{}'".format(type(srv))
            raise TypeError(msg)
        if not isinstance(uid, self.type_uid):
            msg = "'uid' must be of type '{}', ".format(self.type_uid)
            msg += "not '{}'".format(type(uid))
            raise TypeError(msg)
        if not isinstance(data, self.type_data):
            msg = "'metadata' must be of type '{}', ".format(self.type_data)
            msg += "not '{}'".format(type(data))
            raise TypeError(msg)

        # Save Attrs
        self._srv = srv
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

    def exists(self):
        """Secret Exists?"""
        return self._srv.secret_exists(self)

    def rem(self):
        """Delete Secret"""
        self._srv.secret_unregister(self)
        self._data.rem()
