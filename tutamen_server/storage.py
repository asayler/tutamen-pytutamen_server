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

_PREFIX_COLLECTION = "collection"
_PREFIX_SECRET = "secret"

_POSTFIX_DATA = "data"
_POSTFIX_METADATA = "metadata"


### Objects ###

class StorageServer(datatypes.PersistentObjectServer):

    def __init__(self, driver, prefix=_PREFIX_STORAGESERVER):

        # Call Parent
        super().__init__(driver, prefix=prefix)

        # Setup Collections Index
        key = _INDEX_KEY_COLLECTIONS
        self._collections = datatypes.Index(self, key=key, prefix=prefix,
                                            create=True, overwrite=False)

    def destroy(self):

        # Cleanup Indexes
        self._collections.destroy()

        # Call Parent
        super().destroy()

    def collections_create(self, usermetadata={}):
        return Collection(self, create=True, usermetadata=usermetadata)

    def collections_get(self, uid=None, key=None):

        # Check Args
        if not uid and not key:
            raise TypeError("Requires either uid or key")

        # Create
        return Collection(self, create=False, key=key, uid=uid)

    def collections_list(self):
        return self._collections.members

    def collections_exists(self, uid=None, key=None):

        # Check Args
        if not uid and not key:
            raise TypeError("Requires either uid or key")
        if uid:
            datatypes.check_isinstance(uid, uuid.UUID)

        # Convert key
        if not key:
            key = str(uid)

        # Check membership
        return self._collections.is_member(key)

class Collection(datatypes.UUIDObject, datatypes.UserMetadataObject):

    def __init__(self, srv, create=False, overwrite=False,
                 prefix=_PREFIX_COLLECTION, **kwargs):
        """Initialize Collection"""

        # Check Input
        datatypes.check_isinstance(srv, StorageServer)
        if overwrite:
            raise TypeError("Collection does not support overwrite")

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Setup Secret Index
        key = self.key + _INDEX_KEY_SECRETS
        self._secrets = datatypes.Index(self.srv, key=key, prefix=prefix,
                                        create=create, overwrite=overwrite)

        # Register with Server
        if create:
            self.srv._collections.add(self)
        else:
            if not self.srv.collections_exists(key=self.key):
                msg = "Collection not associated with srv"
                raise TypeError(msg)

    def destroy(self):
        """Delete Collection"""

        # Unregister with Server
        self.srv._collections.remove(self)

        # Cleanup Indexes
        self._secrets.destroy()

        # Call Parent
        super().destroy()

    def secrets_create(self, data="", usermetadata={}):
        return Secret(self, create=True, data=data, usermetadata=usermetadata)

    def secrets_get(self, uid=None, key=None):

        # Check Args
        if not uid and not key:
            raise TypeError("Requires either uid or key")

        # Create
        return Secret(self, create=False, key=key, uid=uid)

    def secrets_list(self):
        return self._secrets.members

    def secrets_exists(self, uid=None, key=None):

        # Check Args
        if not uid and not key:
            raise TypeError("Requires either uid or key")
        if uid:
            datatypes.check_isinstance(uid, uuid.UUID)

        # Convert key
        if not key:
            key = str(uid)

        # Check membership
        return self._secrets.is_member(key)

class Secret(datatypes.UUIDObject, datatypes.UserMetadataObject):

    def __init__(self, col, create=False, overwrite=False,
                 prefix=_PREFIX_SECRET, data="", **kwargs):
        """Initialize Secret"""

        # Check Input
        if not isinstance(col, Collection):
            datatypes.check_isinstance(col, Collection)
        if overwrite:
            raise TypeError("Secret does not support overwrite")

        # Call Parent
        super().__init__(col.srv, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Save Collection
        self._col = col

        # Setup Data
        factory = self.srv.make_factory(dso.String, key_type=dsk.StrKey)
        data_key = self._build_key(_POSTFIX_DATA)
        self._data = factory.from_raw(data_key)
        if not self._data.exists():
            if create:
                self._data.create(data)
            else:
                raise ObjectDNE(self)

        # Register with Collection
        if create:
            self.col._secrets.add(self)
        else:
            if not self.col.secrets_exists(key=self.key):
                msg = "Secret not associated with col '{}'".format(self.col.key)
                raise TypeError(msg)

    def destroy(self):
        """Delete Secret"""

        # Unregister with Collection
        self.col._secrets.remove(self)

        # Cleanup Objects
        self._data.rem()

        # Call Parent
        super().destroy()

    @property
    def col(self):
        """Return Collection"""
        return self._col

    @property
    def data(self):
        """Return Secret Data"""
        return self._data.get_val()
