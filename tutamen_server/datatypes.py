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

    def __init__(self, key):

        # Call Parent
        msg = "Object '{:s}' does not exist".format(key)
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

    @classmethod
    @abc.abstractmethod
    def from_new(cls, srv, key, *args, **kwargs):
        return cls(srv, key, *args, **kwargs)

    @classmethod
    @abc.abstractmethod
    def from_existing(cls, srv, key, *args, **kwargs):
        return cls(srv, key, *args, **kwargs)

    @classmethod
    @abc.abstractmethod
    def from_any(cls, srv, key, *args, **kwargs):
        return cls(srv, key, *args, **kwargs)

    def __init__(self, srv, key):
        """Initialize Object"""

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
        pass

    @property
    def key(self):
        return self._key

    @property
    def srv(self):
        return self._srv

### Objects ###

class Index(PersistentObject):

    @classmethod
    def from_new(cls, srv, key, *args, **kwargs):

        # Setup Members
        factory = srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        index_key = key + _INDEX_POSTFIX
        index = factory.from_new(index_key, set())

        # Call parent
        obj = super().from_new(srv, key, *args, index=index, **kwargs)

        return obj

    @classmethod
    def from_existing(cls, srv, key, *args, **kwargs):

        # Setup Members
        factory = srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        index_key = key + _INDEX_POSTFIX
        index = factory.from_existing(index_key)

        # Call parent
        obj = super().from_existing(srv, key, *args, index=index, **kwargs)

        return obj

    @classmethod
    def from_any(cls, srv, key, *args, **kwargs):

        # Setup Members
        factory = srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        index_key = key + _INDEX_POSTFIX
        index = factory.from_raw(index_key)
        if not index.exists():
            index.create(set())

        # Call parent
        obj = super().from_any(srv, key, *args, index=index, **kwargs)

        return obj

    def __init__(self, *args, index=None, **kwargs):
        """Initialize Object"""

        # Check Args
        if not isinstance(index, _INDEX_OBJ_TYPE):
            msg = "'index' must be of type '{}', ".format(_INDEX_OBJ_TYPE)
            msg += "not '{}'".format(type(index))
            raise TypeError(msg)

        # Call Parent
        super().__init__(*args, **kwargs)

        # Save Attrs
        self._index = index

    def destroy(self):

        # Unregister objects
        for obj_key in self.members:
            obj = Indexed.from_any(self._srv, obj_key)
            obj.unregister(self)

        # Cleanup backend object
        self._index.rem()

        # Call Parent
        super().destroy()

    @property
    def members(self):

        # Return index memebership
        return set(self._index)

    def add(self, obj):

        # Check Args
        if not isinstance(obj, Indexed):
            msg = "'obj' must be an instance of '{}', ".format(Indexed)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Add Object Key and Register Index
        obj.register(self)
        self._index.add(obj.key)

    def remove(self, obj):

        # Check Args
        if not isinstance(obj, Indexed):
            msg = "'obj' must be an instance of '{}', ".format(Indexed)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Remove Object Key and Unregister Index
        self._index.discard(obj.key)
        obj.unregister(self)

class Indexed(PersistentObject):

    @classmethod
    def from_new(cls, srv, key, *args, **kwargs):

        # Setup Members
        factory = srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        metaindex_key = key + _METAINDEX_POSTFIX
        metaindex = factory.from_new(metaindex_key, set())

        # Call parent
        obj = super().from_new(srv, key, *args, metaindex=metaindex, **kwargs)

        return obj

    @classmethod
    def from_existing(cls, srv, key, *args, **kwargs):

        # Setup Members
        factory = srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        metaindex_key = key + _METAINDEX_POSTFIX
        metaindex = factory.from_existing(metaindex_key)

        # Call parent
        obj = super().from_existing(srv, key, *args, metaindex=metaindex, **kwargs)

        return obj

    @classmethod
    def from_any(cls, srv, key, *args, **kwargs):

        # Setup Members
        factory = srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        metaindex_key = key + _METAINDEX_POSTFIX
        metaindex = factory.from_raw(metaindex_key)
        if not metaindex.exists():
            metaindex.create(set())

        # Call parent
        obj = super().from_any(srv, key, *args, metaindex=metaindex, **kwargs)

        return obj

    def __init__(self, *args, metaindex=None, **kwargs):
        """Initialize Object"""

        # Check Args
        if not isinstance(metaindex, _INDEX_OBJ_TYPE):
            msg = "'metaindex' must be of type '{}', ".format(_INDEX_OBJ_TYPE)
            msg += "not '{}'".format(type(metaindex))
            raise TypeError(msg)

        # Call Parent
        super().__init__(*args, **kwargs)

        # Save Attrs
        self._metaindex = metaindex

    def destroy(self):

        # Unregister from indexes
        for idx_key in self.indexes:
            index = Index.from_any(self._srv, idx_key)
            index.remove(self)

        # Cleanup metaindex
        self._metaindex.rem()

        # Call Parent
        super().destroy()

    @property
    def indexes(self):

        # Return registered indexes
        return set(self._metaindex)

    def register(self, index):

        # Check Args
        if not isinstance(index, Index):
            msg = "'index' must be an instance of '{}', ".format(Index)
            msg += "not '{}'".format(type(index))
            raise TypeError(msg)

        # Add Index Key
        self._metaindex.add(index.key)

    def unregister(self, index):

        # Check Args
        if not isinstance(index, Index):
            msg = "'index' must be an instance of '{}', ".format(Index)
            msg += "not '{}'".format(type(index))
            raise TypeError(msg)

        # Remove Index Key
        self._metaindex.discard(index.key)
