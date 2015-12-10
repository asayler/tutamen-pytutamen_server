# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as dso
from pcollections import keys as dsk

from . import datatypes


### Constants ###

_INDEX_KEY_SECRETS = "secrets"
_INDEX_KEY_COLLECTIONS = "collections"

_PREFIX_STORAGESERVER = "storagesrv"

_PREFIX_SECRET = "secret"
_POSTFIX_SECRET_DATA = "data"
_POSTFIX_METADATA = "metadata"


### Objects ###

class StorageServer(datatypes.PersistentObjectServer):

    def __init__(self, driver, prefix=_PREFIX_STORAGESERVER):

        # Call Parent
        super().__init__(driver, prefix=prefix)

        # Setup Collections Index
        self._collections = datatypes.Index(self, _INDEX_KEY_COLLECTIONS, prefix=prefix)

    def destroy(self):

        # Cleanup Indexes
        self._collections.destroy()

        # Call Parent
        super().destroy()

    def collections_create(self, metadata={}):
        return Collection(self, create=True, metadata=metadata)
    def collections_get(self, uid):
        return Collection(self, create=False, key=uid)
    def collections_list(self):
        return self._collections.members()
    def collections_exists(self, uid):
        return self._collections.is_member(uid)

class Collection(datatypes.UUIDObject):

    def __init__(self, srv, create=False, overwrite=False,
                 prefix=_PREFIX_COLLECTION, metadata={}, **kwargs):
        """Initialize Collection"""

        # Check Input
        if overwrite:
            raise TypeError("Collection does not support overwrite")

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Setup Metadata
        factory = self.srv.make_factory(dso.MutableDictionary, key_type=dsk.StrKey)
        metadata_key = self._build_key(_POSTFIX_METADATA)
        self._metadata = factory.from_raw(metadata_key)
        if not self._metadata.exists():
            if create:
                self._metadata.create(metadata)

        # Setup Secret Index
        self._secrets = datatypes.Index(self, _INDEX_KEY_SECRETS, prefix=prefix)

        # Register with Server
        if create:
            self.srv._collections.add(self)

    def destroy(self):
        """Delete Collection"""

        # Unregister with Server
        self.srv._collections.remove(self)

        # Cleanup Indexes
        self._secrets.destroy()

        # Cleanup Objects
        self._metadata.rem()

        # Call Parent
        super().destory()

    @property
    def metadata(self):
        """Return Collection Metadata"""
        return self._metadata.get_val()

    def secrets_create(self, data="", metadata={}):
        return Secret(self, create=True, data=data, metadata=metadata)
    def secrets_get(self, uid):
        return Secret(self, create=False, key=uid)
    def secrets_list(self):
        return self._secrets.members()
    def secrets_exists(self, uid):
        return self._secrets.is_member(uid)

class Secret(datatypes.UUIDObject):

    def __init__(self, collection, key=None, create=False, overwrite=False,
                 prefix=_PREFIX_SECRET, data="", metadata={}, **kwargs):
        """Initialize Secret"""

        # Check Input
        if overwrite:
            raise TypeError("Secret does not support overwrite")

        # Call Parent
        super().__init__(collection.srv, key=key, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Save Collection
        self._collection = collection

        # Setup Data
        factory = self.srv.make_factory(dso.String, key_type=dsk.StrKey)
        data_key = self._build_key(_POSTFIX_SECRET_DATA)
        self._data = factory.from_raw(data_key)
        if not self._data.exists():
            if create:
                self._data.create(data)

        # Setup Metadata
        factory = self.srv.make_factory(dso.MutableDictionary, key_type=dsk.StrKey)
        metadata_key = self._build_key(_POSTFIX_METADATA)
        self._metadata = factory.from_raw(metadata_key)
        if not self._metadata.exists():
            if create:
                self._metadata.create(metadata)

        # Register with Collection
        if create:
            self.collection._secrets.add(self)

    def destroy(self):
        """Delete Secret"""

        # Unregister with Collection
        self.collection._secrets.remove(self)

        # Cleanup Objects
        self._metadata.rem()
        self._data.rem()

        # Call Parent
        super().destory()

    @property
    def collection(self):
        """Return Collection"""
        return self._collection

    @property
    def data(self):
        """Return Secret Data"""
        return self._data.get_val()

    @property
    def metadata(self):
        """Return Secret Metadata"""
        return self._metadata.get_val()
