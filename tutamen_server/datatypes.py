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


### Abstarct Objects ###

class PersistentObjectServer(object, metaclass=abc.ABCMeta):

    def __init__(self, driver):

        # Check Args
        # TODO: Verify driver is of appropriate type

        # Call Parent
        super().__init__()

        # Save Attrs
        self._driver = driver

    @property
    def driver(self):
        return self._driver

    @abc.abstractmethod
    def destroy(self):
        pass

    def make_factory(self, obj_type, key_type=dsk.StrKey, key_kwargs={}):
        return dsf.InstanceFactory(self._driver, obj_type,
                                   key_type=key_type, key_kwargs=key_kwargs)

class PersistentObject(object, metaclass=abc.ABCMeta):

    @abc.abstractmethod
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

    @abc.abstractmethod
    def destroy(self):
        """Cleanup Object"""
        pass

    @property
    def key(self):
        """Return Object Key (Read-only Property)"""
        return self._key

    @property
    def srv(self):
        """Return Object Server (Read-only Property)"""
        return self._srv

### Objects ###

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
            obj = Indexed(self._srv, obj_key)
            obj.unregister(self)

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
        if not isinstance(obj, Indexed):
            msg = "'obj' must be an instance of '{}', ".format(Indexed)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Add Object Key and Register Index
        obj.register(self)
        self._index.add(obj.key)

    def remove(self, obj):
        """Remove Indexed Object to Index if Present"""

        # Check Args
        if not isinstance(obj, Indexed):
            msg = "'obj' must be an instance of '{}', ".format(Indexed)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Remove Object Key and Unregister Index
        self._index.discard(obj.key)
        obj.unregister(self)

class Indexed(PersistentObject):

    def __init__(self, *args, create=False, overwrite=False, **kwargs):
        """Initialize Indexed Object"""

        # Call Parent
        super().__init__(*args, create=create, overwrite=overwrite, **kwargs)

        # Setup Metaindex
        factory = self.srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        metaindex_key = self.key + _METAINDEX_POSTFIX
        metaindex = factory.from_raw(metaindex_key)
        if not metaindex.exists():
            if create:
                metaindex.create(set())
            else:
                raise ObjectDNE(self)
        else:
            if create and overwrite:
                metaindex.set_val(set())

        # Save Attrs
        self._metaindex = metaindex

    def destroy(self):
        """Cleanup Indexed Object"""

        # Unregister from indexes
        for idx_key in self.indexes:
            index = Index(self._srv, idx_key)
            index.remove(self)

        # Cleanup metaindex
        self._metaindex.rem()

        # Call Parent
        super().destroy()

    @property
    def indexes(self):
        """Return Registered Indexes"""

        # Return registered indexes
        return set(self._metaindex)

    def register(self, index):
        """Register Index"""

        # Check Args
        if not isinstance(index, Index):
            msg = "'index' must be an instance of '{}', ".format(Index)
            msg += "not '{}'".format(type(index))
            raise TypeError(msg)

        # Add Index Key
        self._metaindex.add(index.key)

    def unregister(self, index):
        """Unregister Index if Registered"""

        # Check Args
        if not isinstance(index, Index):
            msg = "'index' must be an instance of '{}', ".format(Index)
            msg += "not '{}'".format(type(index))
            raise TypeError(msg)

        # Remove Index Key
        self._metaindex.discard(index.key)
