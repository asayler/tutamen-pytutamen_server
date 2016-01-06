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

_USERDATA_POSTFIX = "userdata"


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

def build_pkey(base_key, prefix=None, postfix=None):

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

class PersistentObject(object):

    def __init__(self, pbackend, key=None, prefix="", create=False):

        #                      create
        # OPEN_EXISTING        False
        # CREATE_OR_OPEN       True

        # Check args
        check_isinstance(pbackend, backends.Backend)
        check_isinstance(key, str)
        check_isinstance(prefix, str)

        # Call Parent
        super().__init__()

        # Save Attrs
        self._pbackend = pbackend
        self._pcollections = collections.PCollections(pbackend)
        self._key = key
        self._prefix = prefix

    def destroy(self):
        pass

    @property
    def pbackend(self):
        return self._pbackend

    @property
    def pcollections(self):
        return self._pcollections

    @property
    def key(self):
        return self._key

    @property
    def prefix(self):
        return self._prefix

    def __repr__(self):
        return "{:s}_{:s}".format(type(self).__name__, self.key)

    def __hash__(self):
        return hash(self.key)

    def __eq__(self, other):
        if type(other) == type(self):
            return self.key == other.key
        else:
            return False

    def _build_pkey(self, postfix):
        return build_pkey(self.key, prefix=self.prefix, postfix=postfix)

    def _build_pobj(self, obj_type, postfix, create=None):

        #                      create
        # OPEN_EXISTING         None
        # CREATE_OR_OPEN        Val

        pkey = self._build_pkey(postfix=postfix)
        pobj = obj_type(pkey, create=create, existing=None)
        if not pobj.exists():
            raise ObjectDNE(pobj)
        return pobj

    def val_to_key(self, val):

        if isinstance(val, str):
            return val
        elif isinstance(val, uuid.UUID):
            return str(val)
        elif isinstance(val, PersistentObject):
            return val.key
        else:
            raise TypeError("val must be a str, uuid.UUID, or PersistentObject")

    def val_to_uid(self, val):

        if isinstance(val, uuid.UUID):
            return val
        elif isinstance(val, str):
            return uuid.UUID(val)
        elif isinstance(val, UUIDObject):
            return val.uid
        else:
            raise TypeError("val must be a uuid.UUID, str, or UUIDObject")

    def val_to_obj(self, val, obj_type, **kwargs):

        if isinstance(val, obj_type):
            return val
        elif isinstance(val, str):
            if issubclass(obj_type, PersistentObject):
                return obj_type(self.pbackend, key=val, **kwargs)
            else:
                raise TypeError("val can not be str unless obj_type is PersistentObject")
        elif isinstance(val, uuid.UUID):
            if issubclass(obj_type, UUIDObject):
                return obj_type(self.pbackend, uid=val, **kwargs)
            else:
                raise TypeError("val can not be uuid.UUID unless obj_type is UUIDObject")
        else:
            raise TypeError("val must be an {}, str, or uuid.UUID".format(obj_type))

class UUIDObject(PersistentObject):

    def __init__(self, srv, key=None, uid=None, create=False, **kwargs):
        """Initialize Object"""

        #                      create
        # OPEN_EXISTING        False
        # CREATE_OR_OPEN       True

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
                    raise TypeError("Requires either uid or key")
            else:
                key = str(uid)
        if not uid:
            uid = uuid.UUID(key)

        # Call Parent
        super().__init__(srv, key=key, create=create, **kwargs)

        # Save UUID
        self._uid = uid

    @property
    def uid(self):
        return self._uid

class UserDataObject(PersistentObject):

    def __init__(self, pbackend, create=False, userdata={}, **kwargs):
        """Initialize Object"""

        # Call Parent
        super().__init__(pbackend, create=create, **kwargs)

        # Setup Metadata
        self._userdata = self._build_pobj(self.pcollections.MutableDictionary,
                                          _USERDATA_POSTFIX,
                                          create=userdata)

    def destroy(self):
        """Cleanup Object"""

        # Cleanup pbackend object
        self._userdata.rem()

        # Call Parent
        super().destroy()

    @property
    def userdata(self):
        return self._userdata.get_val()

class ServerObject(PersistentObject):

    def __init__(self, pbackend, prefix="srv", **kwargs):

        # Call Parent
        super().__init__(pbackend, prefix=prefix, **kwargs)

    def destroy(self):

        # Call Parent
        super().destroy()

class ChildObject(PersistentObject):

    def __init__(self, pbackend, create=False, pindex=None, **kwargs):
        """Initialize Child"""

        #                      create
        # OPEN_EXISTING        False
        # CREATE_OR_OPEN       True

        # Check Input
        check_isinstance(pindex, ChildIndex)
        if pindex.parent.pbackend != pbackend:
            raise TypeError("parent and child must have common pbackend")

        # Call Parent
        super().__init__(pbackend, create=create, **kwargs)

        # Setup Vars
        self._pindex = pindex

        # Register with Index
        if create:
            self._pindex._children.add(self.key)
        else:
            if not self._pindex.exists(self.key):
                raise ObjectDNE(self)

    def destroy(self):
        """Cleanup Object"""

        # Unregister with Index
        self._pindex._children.discard(self.key)

        # Call Parent
        super().destroy()

    @property
    def pindex(self):
        return self._pindex

    @property
    def parent(self):
        return self._pindex.parent

    def exists(self):
        return self._pindex.exists(self.key)

class ChildIndex(object):

    def __init__(self, parent, type_child, label):
        """Initialize Child Index"""

        # Call Parent
        super().__init__()

        # Check Args
        check_isinstance(parent, PersistentObject)
        check_issubclass(type_child, ChildObject)
        check_isinstance(label, str)

        # Save Args
        self._parent = parent
        self._type_child = type_child
        self._label = label

        # Setup Index Set
        self._children = parent._build_pobj(self.parent.pcollections.MutableSet,
                                            label, create=set())

    def destroy(self):
        """Cleanup Index"""

        # ToDo: Delete children?

        # Cleanup Set
        self._children.rem()

    @property
    def parent(self):
        return self._parent

    @property
    def type_child(self):
        return self._type_child

    def __len__(self):
        return len(self._children)

    def create(self, **kwargs):
        return self.type_child(self.parent.pbackend, pindex=self, create=True, **kwargs)

    def get(self, **kwargs):
        return self.type_child(self.parent.pbackend, pindex=self, create=False, **kwargs)

    def exists(self, val):
        key = self.parent.val_to_key(val)
        return key in self._children

    def by_key(self):
        return self._children.get_val()

    def by_uid(self):
        return set([self.parent.val_to_uid(key)
                    for key in self._children])

    def by_obj(self):
        return set([self.parent.val_to_obj(key, self.type_child, pindex=self)
                    for key in self._children])

class Index(PersistentObject):

    def __init__(self, pbackend, create=False, **kwargs):
        """Initialize Index Object"""

        # Call Parent
        super().__init__(pbackend, create=create, **kwargs)

        # Setup Index
        self._index = self._build_pobj(self.pcollections.MutableSet,
                                       _INDEX_POSTFIX, create=set())

    def destroy(self):
        """Cleanup Index Object"""

        # Cleanup pbackend object
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
