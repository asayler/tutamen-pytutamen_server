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
_OBJINDEX_POSTFIX = "objindex"
_OBJINDEX_KEY = "objects"

_USERMETADATA_POSTFIX = "usermetadata"


### Exceptions ###

class ObjectDNE(Exception):

    def __init__(self, obj):

        # Check Args
        if not isinstance(obj, PersistentObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Call Parent
        msg = "Object '{}' does not exist".format(obj.key)
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

def check_isinstance(obj, cls):

    if not isinstance(obj, cls):
        msg = "Object must be of type '{}', not '{}'".format(cls, type(obj))
        raise TypeError(msg)

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
        check_isinstance(obj, PersistentObject)

        # Add Object key
        self._objindex.add(obj.key)

    def _unregister(self, obj):

        # Check Args
        check_isinstance(obj, PersistentObject)

        # Discard Object Key
        self._objindex.discard(obj.key)

    def make_factory(self, obj_type, key_type=dsk.StrKey, key_kwargs={}):
        return dsf.InstanceFactory(self._driver, obj_type,
                                   key_type=key_type, key_kwargs=key_kwargs)

class PersistentObject(object):

    def __init__(self, srv, key=None, create=False, overwrite=False, prefix=""):
        """Initialize Object"""

        #                    create  overwrite  existing
        # CREATE_OR_OPEN       Y         N         Y
        # CREATE_OVERWRITE     Y         Y         Y
        # CREATE_OR_FAIL       Y         *         N
        # OPEN_EXISTING        N         *         *

        # Check Args
        check_isinstance(srv, PersistentObjectServer)
        check_isinstance(key, str)
        check_isinstance(prefix, str)
        if not key:
            msg = "Requires valid key"
            raise TypeError(msg)
            raise TypeError(msg)

        # Call Parent
        super().__init__()

        # Save Attrs
        self._srv = srv
        self._key = key
        self._prefix = prefix

        # Check Existence
        if not self.exists():
            if not create:
                raise ObjectDNE(self)

        # Register with Server
        self.srv._register(self)

    def _build_key(self, postfix):
        return build_key(self.key, prefix=self.prefix, postfix=postfix)

    def destroy(self):
        """Cleanup Object"""

        # Unregister from server
        self.srv._unregister(self)

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

class UUIDObject(PersistentObject):

    def __init__(self, srv, key=None, uid=None, **kwargs):
        """Initialize Object"""

        # Check Args
        if key:
            check_isinstance(key, str)
        if uid:
            check_isinstance(uid, uuid.UUID)

        # Setup key and uid
        if not key:
            if not uid:
                uid = uuid.uuid4()
                key = str(uid)
            else:
                key = str(uid)
        if not uid:
            uid = uuid.UUID(key)

        # Call Parent
        super().__init__(srv, key=key, **kwargs)

        # Save UUID
        self._uid = uid

    @property
    def uid(self):
        return self._uid

class UserMetadataObject(PersistentObject):

    def __init__(self, srv, create=False, overwrite=False, usermetadata={}, **kwargs):
        """Initialize Object"""

        # Check Args
        check_isinstance(usermetadata, dict)
        if overwrite:
            raise TypeError("UserMetadataObject does not support overwrite")

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite, **kwargs)

        # Setup Metadata
        factory = self.srv.make_factory(dso.MutableDictionary, key_type=dsk.StrKey)
        usermetadata_key = self._build_key(_USERMETADATA_POSTFIX)
        self._usermetadata = factory.from_raw(usermetadata_key)
        if not self._usermetadata.exists():
            if create:
                self._usermetadata.create(usermetadata)
            else:
                raise ObjectDNE(self)

    def destroy(self):
        """Cleanup Object"""

        # Cleanup backend object
        self._usermetadata.rem()

        # Call Parent
        super().destroy()

    @property
    def usermetadata(self):
        return self._usermetadata.get_val()

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
