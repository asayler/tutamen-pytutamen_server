# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import abc
import uuid


from pcollections import backends
from pcollections import collections


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

def nos(val):
    """ None or Str"""
    return str(val) if val is not None else None


### Objects ###

class PersistentObjectServer(object):

    def __init__(self, backend, prefix="srv"):

        # Check args
        check_isinstance(backend, backends.Backend)

        # Call Parent
        super().__init__()

        # Save Attrs
        self._backend = backend
        self._collections = collections.PCollections(backend)
        self._prefix = prefix

        # Setup Object Index
        self._objindex = self._build_subobj(self.collections.MutableSet,
                                            _OBJINDEX_KEY, postfix=_OBJINDEX_POSTFIX,
                                            create=set())

    def destroy(self):

        # Cleanup Object Index
        self._objindex.rem()

    def _build_subkey(self, base_key, postfix=None):
        return build_key(base_key, prefix=self.prefix, postfix=postfix)

    def _build_subobj(self, obj_type, base_key, postfix=None, create=None):

        #                      create
        # OPEN_EXISTING         None
        # CREATE_OR_OPEN        Val

        subkey = self._build_subkey(base_key, postfix=postfix)
        obj = obj_type(subkey, create=create, existing=None)
        if not obj.exists():
            raise ObjectDNE(obj)
        return obj

    @property
    def backend(self):
        return self._backend

    @property
    def collections(self):
        return self._collections

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

class PersistentObject(object):

    def __init__(self, srv, key=None, create=False, prefix=""):
        """Initialize Object"""

        #                      create
        # OPEN_EXISTING        False
        # CREATE_OR_OPEN       True

        # Check Args
        check_isinstance(srv, PersistentObjectServer)
        check_isinstance(key, str)
        check_isinstance(create, bool)
        check_isinstance(prefix, str)
        if not key:
            msg = "Requires valid key"
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

    def _build_subobj(self, obj_type, postfix, create=None):

        #                      create
        # OPEN_EXISTING         None
        # CREATE_OR_OPEN        Val

        subkey = self._build_subkey(postfix)
        obj = obj_type(subkey, create=create, existing=None)
        if not obj.exists():
            raise ObjectDNE(obj)
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

    def _val_to_key(self, val, obj=None):

        if obj is None:
            obj = type(self)
        else:
            check_issubclass(obj, PersistentObject)

        if isinstance(val, obj):
            return val.key
        elif isinstance(val, str):
            return val
        else:
            raise TypeError("val must be an {} or str".format(obj))

    def _val_to_obj(self, val, obj=None):

        if obj is None:
            obj = type(self)
        else:
            check_issubclass(obj, PersistentObject)

        if isinstance(val, obj):
            return val
        elif isinstance(val, str):
            return obj(self.srv, key=val, create=False)
        else:
            raise TypeError("val must be an {} or str".format(obj))

    def exists(self):
        return self.srv.exists(self.key)

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

    def __init__(self, srv, key=None, uid=None, create=False, **kwargs):
        """Initialize Object"""

        # Check Args
        if key:
            check_isinstance(key, str)
        if uid:
            check_isinstance(uid, uuid.UUID)

        # Setup key and uid
        if not key:
            if not uid:
                if create:
                    uid = uuid.uuid4()
                    key = str(uid)
                else:
                    raise TyepError("Requires either uid or key")
            else:
                key = str(uid)
        if not uid:
            uid = uuid.UUID(key)

        # Call Parent
        super().__init__(srv, key=key, create=create, **kwargs)

        # Save UUID
        self._uid = uid

    def _val_to_key(self, val, obj=None):

        if obj is None:
            obj = type(self)
        else:
            check_issubclass(obj, UUIDObject)

        if isinstance(val, obj):
            return val.key
        elif isinstance(val, uuid.UUID):
            return str(val)
        elif isinstance(val, str):
            return val
        else:
            raise TypeError("val must be an {} or str".format(obj))

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
            raise TypeError("val must be an {}, uuid, or str".format(obj))

    def _val_to_uid(self, val, obj=None):

        if obj is None:
            obj = type(self)
        else:
            check_issubclass(obj, UUIDObject)

        if isinstance(val, obj):
            return val.uid
        elif isinstance(val, uuid.UUID):
            return val
        elif isinstance(val, str):
            return uuid.UUID(val)
        else:
            raise TypeError("val must be an {}, uuid, or str".format(obj))

    @property
    def uid(self):
        return self._uid

class UserMetadataObject(PersistentObject):

    def __init__(self, srv, create=False, usermetadata={}, **kwargs):
        """Initialize Object"""

        # Call Parent
        super().__init__(srv, create=create, **kwargs)

        # Setup Metadata
        self._usermetadata = self._build_subobj(self.srv.collections.MutableDictionary,
                                                _USERMETADATA_POSTFIX,
                                                create=usermetadata)

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

    def __init__(self, srv, create=False, **kwargs):
        """Initialize Index Object"""

        # Call Parent
        super().__init__(srv, create=create, **kwargs)

        # Setup Index
        self._index = self._build_subobj(self.srv.collections.MutableSet,
                                         _INDEX_POSTFIX, create=set())

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
