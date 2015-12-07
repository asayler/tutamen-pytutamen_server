# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as dso
from pcollections import keys as dsk

from . import datatypes


### Constants ###

SEPERATOR = datatypes.SEPERATOR

_INDEX_KEY_SECRETS = "secrets"
_INDEX_KEY_COLLECTIONS = "collections"

_PREFIX_STORAGESERVER = "storagesrv"

_PREFIX_SECRET = "secret"
_POSTFIX_SECRET_DATA = "data"
_POSTFIX_SECRET_METADATA = "metadata"


### Exceptions ###



### Objects ###

class StorageServer(datatypes.PersistentObjectServer):

    def __init__(self, driver, prefix=_PREFIX_STORAGESERVER):

        # Call Parent
        super().__init__(driver, prefix=prefix)

        # Setup Server Indexes
        self._index_secrets = datatypes.Index(self, _INDEX_KEY_SECRETS, prefix=prefix)
        self._index_collections = datatypes.Index(self, _INDEX_KEY_COLLECTIONS, prefix=prefix)

    def destroy(self):

        # Cleanup Indexes
        self._index_secrets.destroy()
        self._index_collections.destroy()

        # Call Parent
        super().destroy()

class Secret(datatypes.PersistentObject):

    def __init__(self, *args, create=False, overwrite=False, prefix=_PREFIX_SECRET,
                 data="", metadata={}, **kwargs):
        """Initialize Secret"""

        # Check Input
        if overwrite:
            raise TypeError("Secret does not support overwrite")

        # Call Parent
        super().__init__(*args, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Setup Data
        factory = self.srv.make_factory(dso.String, key_type=dsk.StrKey)
        data_key = self.prefix + SEPERATOR + self.key + SEPERATOR + _POSTFIX_SECRET_DATA
        self._data = factory.from_raw(data_key)
        if not self._data.exists():
            if create:
                self._data.create(data)

        # Setup Metadata
        factory = self.srv.make_factory(dso.MutableDictionary, key_type=dsk.StrKey)
        metadata_key = self.prefix + SEPERATOR + self.key + SEPERATOR + _POSTFIX_SECRET_METADATA
        self._metadata = factory.from_raw(metadata_key)
        if not self._metadata.exists():
            if create:
                self._metadata.create(metadata)

    def destroy(self):
        """Delete Secret"""

        # Cleanup Objects
        self._metadata.rem()
        self._data.rem()

        # Call Parent
        super().destory()

    @property
    def data(self):
        """Return Secret Data"""
        return self._data.get_val()

    @property
    def metadata(self):
        """Return Secret Metadata"""
        return self._metadata.get_val()
