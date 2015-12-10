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

_SEPERATOR = "_"
_INDEX_OBJ_TYPE = dso.MutableSet
_INDEX_KEY_TYPE = dsk.StrKey
_INDEX_POSTFIX = "index"
_METAINDEX_POSTFIX = "metaindex"
_OBJINDEX_POSTFIX = "objindex"
_OBJINDEX_KEY = "objects"


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

### Functions ###

def build_key(base_key, prefix=None, postfix=None):

    key = str()
    if prefix is not None:
        key += str(prefix) + _SEPERATOR
    key += str(base_key)
    if postfix is not None:
        key += _SEPERATOR + str(postfix)

    return key

### Objects ###

class PersistentObjectServer(object):

    def __init__(self, driver, prefix="srv"):

        # Check Args
        # TODO: Verify driver is of appropriate type

        # Call Parent
        super().__init__()

        # Save Attrs
        self._driver = driver
        self._prefix = prefix

        # Setup Object Index
        factory = self.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        objidx_key = self._build_key(_OBJINDEX_KEY, postfix=_OBJINDEX_POSTFIX)
        objidx = factory.from_raw(objidx_key)
        if not objidx.exists():
            objidx.create(set())
        self._objindex = objidx

    def destroy(self):

        # Cleanup Object Index
        self._objindex.rem()

    def _build_key(self, base_key, postfix=None):
        return build_key(base_key, prefix=self.prefix, postfix=postfix)

    @property
    def driver(self):
        return self._driver

    @property
    def prefix(self):
        return self._prefix

    @property
    def objects(self):
        return self._objindex.get_val()

    def exists(self, key):
        return str(key) in self._objindex

    def _register(self, obj):

        # Check Args
        if not isinstance(obj, PersistentObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Add Object key
        self._objindex.add(str(obj.key))

    def _unregister(self, obj):

        # Check Args
        if not isinstance(obj, PersistentObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Discard Object Key
        self._objindex.discard(str(obj.key))

    def make_factory(self, obj_type, key_type=dsk.StrKey, key_kwargs={}):
        return dsf.InstanceFactory(self._driver, obj_type,
                                   key_type=key_type, key_kwargs=key_kwargs)

class PersistentObject(object):

    def __init__(self, srv, key=None, create=False, overwrite=False, prefix="obj"):
        """Initialize Object"""

        #                    create  overwrite  existing
        # CREATE_OR_OPEN       Y         N         Y
        # CREATE_OVERWRITE     Y         Y         Y
        # CREATE_OR_FAIL       Y         *         N
        # OPEN_EXISTING        N         *         *

        # Check Args
        if not isinstance(srv, PersistentObjectServer):
            msg = "'srv' must be of type '{}', ".format(PersistentObjectServer)
            msg += "not '{}'".format(type(srv))
            raise TypeError(msg)
        if not key:
            msg = "Requires valid key"
            raise TypeError(msg)

        # Call Parent
        super().__init__()

        # Save Attrs
        self._srv = srv
        self._key = key
        self._prefix = prefix

        # Setup Metaindex
        factory = self.srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        metaindex_key = self._build_key(_METAINDEX_POSTFIX)
        metaindex = factory.from_raw(metaindex_key)
        self._metaindex = metaindex

        # Initialize
        if not self.exists():
            if create:
                self.__create__()
            else:
                raise ObjectDNE(self)
        else:
            if create and overwrite:
                self.__create__()

        # Register with Server
        self.srv._register(self)

    def __create__(self):

        if not self._metaindex.exists():
            self._metaindex.create(set())
        else:
            self._metaindex.set_val(set())

    def _build_key(self, postfix):
        return build_key(self.key, prefix=self.prefix, postfix=postfix)

    def destroy(self):
        """Cleanup Object"""

        # Unregister from indexes
        for idx_key in self.indexes:
            index = Index(self._srv, key=idx_key)
            index.remove(self)

        # Unregister from server
        self.srv._unregister(self)

        # Cleanup metaindex
        self._metaindex.rem()

    def exists(self):
        return self._srv.exists(self.key)

    @property
    def key(self):
        """Return Object Key (Read-only Property)"""
        return self._key

    @property
    def prefix(self):
        """Return Object Prefix (Read-only Property)"""
        return self._prefix

    @property
    def srv(self):
        """Return Object Server (Read-only Property)"""
        return self._srv

    @property
    def indexes(self):
        """Return Registered Indexes"""

        # Return registered indexes
        return set(self._metaindex)

class UUIDObject(PersistentObject):

    def __init__(self, srv, key=None, **kwargs):
        """Initialize Object"""

        # Check Args
        if not key:
            key = uuid.uuid4()
        else:
            if not isinstance(key, uuid.UUID):
                msg = "'key' must be an instance of '{}', ".format(uuid.UUID)
                msg += "not '{}'".format(type(key))
                raise TypeError(msg)

        # Call Parent
        super().__init__(srv, key=key, **kwargs)

class Index(PersistentObject):

    def __init__(self, srv, create=False, overwrite=False, **kwargs):
        """Initialize Index Object"""

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite, **kwargs)

        # Setup Index
        factory = self.srv.make_factory(_INDEX_OBJ_TYPE, key_type=_INDEX_KEY_TYPE)
        index_key = self._build_key(_INDEX_POSTFIX)
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
            obj = PersistentObject(self._srv, key=obj_key)
            obj._metaindex.discard(str(self.key))

        # Cleanup backend object
        self._index.rem()

        # Call Parent
        super().destroy()

    @property
    def members(self):
        """Return Index Memebership"""

        return set(self._index)

    def is_member(self, key):
        """Check if object key is in index"""
        return str(key) in self._index

    def add(self, obj):
        """Add Indexed Object to Index"""

        # Check Args
        if not isinstance(obj, PersistentObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Add Object Key and Register Index
        obj._metaindex.add(str(self.key))
        self._index.add(str(obj.key))

    def remove(self, obj):
        """Remove Indexed Object to Index if Present"""

        # Check Args
        if not isinstance(obj, PersistentObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Remove Object Key and Unregister Index
        self._index.discard(str(obj.key))
        obj._metaindex.discard(str(self.key))
