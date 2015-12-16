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
        msg = "'{}' is not an instance of '{}'".format(type(obj), cls)
        raise TypeError(msg)

def check_issubclass(sub, sup):

    if not issubclass(sub, sup):
        msg = "'{}' is not a subclass of '{}'".format(sub, sup)
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
        self._objindex = self._build_subobj(dso.MutableSet,
                                            _OBJINDEX_KEY, postfix=_OBJINDEX_POSTFIX,
                                            create=True, value=set())

    def destroy(self):

        # Cleanup Object Index
        self._objindex.rem()

    def _build_subkey(self, base_key, postfix=None):
        return build_key(base_key, prefix=self.prefix, postfix=postfix)

    def _build_subobj(self, obj_type, base_key, postfix=None, create=False, value=None):

        factory = self.make_factory(obj_type)
        subkey = self._build_subkey(base_key, postfix=postfix)
        obj = factory.from_raw(subkey)

        if not obj.exists():
            if create:
                obj.create(value)
            else:
                raise ObjectDNE(self)

        return obj

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

    def _build_subkey(self, postfix):
        return build_key(self.key, prefix=self.prefix, postfix=postfix)

    def _build_subobj(self, obj_type, postfix, create=False, value=None):

        factory = self.srv.make_factory(obj_type)
        subkey = self._build_subkey(postfix)
        obj = factory.from_raw(subkey)

        if not obj.exists():
            if create:
                obj.create(value)
            else:
                raise ObjectDNE(self)

        return obj

    def __repr__(self):
        return "{:s}_{:s}".format(type(self).__name__, self.key)

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        if isinstance(other, type(self)):
            return self.key == other.key
        else:
            return False

    def destroy(self):
        """Cleanup Object"""

        # Unregister from server
        self.srv._unregister(self)

    def _val_to_key(self, val):

        if isinstance(val, type(self)):
            return val.key
        elif isinstance(val, str):
            return val
        else:
            raise TypeError("val must be an {} or str".format(type(self)))

    def _val_to_obj(self, val, obj=None):

        if obj is None:
            obj = type(self)
        else:
            check_issubclass(obj, PersistentObject)

        if isinstance(val, type(self)):
            return val
        elif isinstance(val, str):
            return obj(self.srv, key=val, create=False)
        else:
            raise TypeError("val must be an {} or str".format(type(self)))

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

    def _val_to_key(self, val):

        if isinstance(val, type(self)):
            return val.key
        elif isinstance(val, uuid.UUID):
            return str(val)
        elif isinstance(val, str):
            return val
        else:
            raise TypeError("val must be an {} or str".format(type(self)))

    def _val_to_obj(self, val, obj=None):

        if obj is None:
            obj = type(self)
        else:
            check_issubclass(obj, UUIDObject)

        if isinstance(val, obj):
            return val
        elif isinstance(val, uuid.UUID):
            return obj(self.srv, uid=val, create=False)
        elif isinstance(val, str):
            return obj(self.srv, key=val, create=False)
        else:
            raise TypeError("val must be an {}, uuid, or str".format(type(self)))

    def _val_to_uid(self, val):

        if isinstance(val, type(self)):
            return val.uid
        elif isinstance(val, uuid.UUID):
            return val
        elif isinstance(val, str):
            return uuid.UUID(val)
        else:
            raise TypeError("val must be an {}, uuid, or str".format(type(self)))

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
        self._usermetadata = self._build_subobj(dso.MutableDictionary, _USERMETADATA_POSTFIX,
                                                create=create, value=usermetadata)

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

        # Check Args
        if overwrite:
            raise TypeError("Index does not support overwrite")

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite, **kwargs)

        # Setup Index
        self._index = self._build_subobj(dso.MutableSet, _INDEX_POSTFIX,
                                         create=create, value=set())

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
