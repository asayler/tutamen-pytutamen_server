# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import abc
import uuid

from pcollections import be_redis_atomic as dso
from pcollections import factories as dsf
from pcollections import keys as dsk


### Constants ###

_INDEX_OBJ_TYPE = dso.MutableSet
_INDEX_KEY_TYPE = dsk.StrKey
_METAINDEX_POSTFIX = "_metaindex"
_INDEX_POSTFIX = "_index"
_SERVER_PREFIX = "srv_"
_OBJECT_INDEX_KEY = "object"


### Exceptions ###

class ObjectDNE(Exception):

    def __init__(self, obj):

        # Check Args
        if not isinstance(obj, PersistentObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Call Parent
        msg = "Object '{:s}' does not exist".format(obj.key)
        super().__init__(msg)


### Objects ###

class PersistentObjectServer(object):

    def __init__(self, driver):

        # Check Args
        # TODO: Verify driver is of appropriate type

        # Call Parent
        super().__init__()

        # Save Attrs
        self._driver = driver

        # Setup Object Index
        key = _SERVER_PREFIX + _OBJECT_INDEX_KEY
        self._objindex = Index(self, key, create=True, overwrite=False)

    @property
    def driver(self):
        return self._driver

    def destroy(self):

        # Cleanup Object Index
        self._objindex.destroy()

    def make_factory(self, obj_type, key_type=dsk.StrKey, key_kwargs={}):
        return dsf.InstanceFactory(self._driver, obj_type,
                                   key_type=key_type, key_kwargs=key_kwargs)

class PersistentObject(object):

    def __init__(self, srv, key, create=False, overwrite=False):
        """Initialize Object"""

        #                    create  overwrite
        # CREATE_OR_OPEN       Y         N
        # CREATE_OVERWRITE     Y         Y
        # OPEN_EXISTING        N         N
        # ?????????????        N         Y

        # Check Args
        if not isinstance(srv, PersistentObjectServer):
            msg = "'srv' must be of type '{}', ".format(PersistentObjectServer)
            msg += "not '{}'".format(type(srv))
            raise TypeError(msg)

        # Call Parent
        super().__init__()

        # Save Attrs
        self._srv = srv
        self._key = key

        # Setup Metaindex
        factory = srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        metaindex_key = key + _METAINDEX_POSTFIX
        metaindex = factory.from_raw(metaindex_key)
        if not metaindex.exists():
            if create:
                metaindex.create(set())
            else:
                raise ObjectDNE(self)
        else:
            if create and overwrite:
                metaindex.set_val(set())
        self._metaindex = metaindex

    def destroy(self):
        """Cleanup Object"""

        # Unregister from indexes
        for idx_key in self.indexes:
            index = Index(self._srv, idx_key)
            index.remove(self)

        # Cleanup metaindex
        self._metaindex.rem()

    @property
    def key(self):
        """Return Object Key (Read-only Property)"""
        return self._key

    @property
    def srv(self):
        """Return Object Server (Read-only Property)"""
        return self._srv

    @property
    def indexes(self):
        """Return Registered Indexes"""

        # Return registered indexes
        return set(self._metaindex)

class Index(PersistentObject):

    def __init__(self, *args, create=False, overwrite=False, **kwargs):
        """Initialize Index Object"""

        # Call Parent
        super().__init__(*args, create=create, overwrite=overwrite, **kwargs)

        # Setup Index
        factory = self.srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        index_key = self.key + _INDEX_POSTFIX
        index = factory.from_raw(index_key)
        if not index.exists():
            if create:
                index.create(set())
            else:
                raise ObjectDNE(self)
        else:
            if create and overwrite:
                index.set_val(set())

        # Save Attrs
        self._index = index

    def destroy(self):
        """Cleanup Index Object"""

        # Unregister objects
        for obj_key in self.members:
            obj = PersistentObject(self._srv, obj_key)
            obj._metaindex.discard(self.key)

        # Cleanup backend object
        self._index.rem()

        # Call Parent
        super().destroy()

    @property
    def members(self):
        """Return Index Memebership"""

        return set(self._index)

    def add(self, obj):
        """Add Indexed Object to Index"""

        # Check Args
        if not isinstance(obj, PersistentObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Add Object Key and Register Index
        obj._metaindex.add(self.key)
        self._index.add(obj.key)

    def remove(self, obj):
        """Remove Indexed Object to Index if Present"""

        # Check Args
        if not isinstance(obj, PersistentObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Remove Object Key and Unregister Index
        self._index.discard(obj.key)
        obj._metaindex.discard(self.key)
