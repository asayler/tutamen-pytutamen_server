# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from . import datatypes


### Constants ###

_INDEX_KEY_SECRETS = "secrets"
_INDEX_KEY_COLLECTIONS = "collections"

_KEY_STORAGESRV = "storage"

_PREFIX_COLLECTION = "collection"
_PREFIX_SECRET = "secret"

_POSTFIX_DATA = "data"


### Objects ###

class StorageServer(datatypes.ServerObject):

    def __init__(self, pbackend, key=_KEY_STORAGESRV):

        # Call Parent
        super().__init__(pbackend, key=key)

        # Setup Collections Index
        self._collections = datatypes.ChildIndex(self, Collection, _INDEX_KEY_SECRETS)

    def destroy(self):

        # Cleanup Indexes
        self._collections.destroy()

        # Call Parent
        super().destroy()

    @property
    def collections(self):
        return self._collections

class Collection(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, prefix=_PREFIX_COLLECTION, **kwargs):
        """Initialize Collection"""

        # Check Input
        datatypes.check_isinstance(pindex.parent, StorageServer)

        # Call Parent
        super().__init__(pbackend, pindex=pindex, prefix=prefix, **kwargs)

        # Setup Secret Index
        self._secrets = datatypes.ChildIndex(self, Secret, _INDEX_KEY_SECRETS)

    def destroy(self):
        """Delete Collection"""

        # Cleanup Indexes
        self._secrets.destroy()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.parent

    @property
    def secrets(self):
        return self._secrets

class Secret(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False, prefix=_PREFIX_SECRET,
                 data="", **kwargs):
        """Initialize Secret"""

        # Check Input
        datatypes.check_isinstance(pindex.parent, Collection)
        if create:
            datatypes.check_isinstance(data, str)

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Data
        self._data = self._build_pobj(self.pcollections.String, _POSTFIX_DATA, create=data)

    def destroy(self):
        """Delete Secret"""

        # Cleanup Objects
        self._data.rem()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.collection.server

    @property
    def collection(self):
        """Return Collection"""
        return self.parent

    @property
    def data(self):
        """Return Secret Data"""
        return self._data.get_val()
