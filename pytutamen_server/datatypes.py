# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import abc
import uuid

from pcollections import abc_base
from pcollections import backends
from pcollections import collections

from . import utility


### Constants ###

_SEPERATOR = "_"

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

class ObjectExists(Exception):

    def __init__(self, obj):

        # Check Args
        if not isinstance(obj, ChildObject):
            msg = "'obj' must be an instance of '{}', ".format(PersistentObject)
            msg += "not '{}'".format(type(obj))
            raise TypeError(msg)

        # Call Parent
        msg = "Object '{}' already exists in parent '{}'".format(obj, obj.parent)
        super().__init__(msg)

class PObjectDNE(Exception):

    def __init__(self, pobj):

        # Check Args
        if not isinstance(pobj, abc_base.Persistent):
            msg = "'pobj' must be an instance of '{}', ".format(abc_base.Persistent)
            msg += "not '{}'".format(type(pobj))
            raise TypeError(msg)

        # Call Parent
        msg = "PObject '{}' does not exist".format(pobj.key)
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


### Objects ###

class PersistentObject(object):

    def __init__(self, pbackend, key=None, prefix=None, create=False):

        #                      create
        # OPEN_EXISTING        False
        # CREATE_OR_OPEN       True

        # Check args
        utility.check_isinstance(pbackend, backends.Backend)
        utility.check_isinstance(key, str)
        if prefix is not None:
            utility.check_isinstance(prefix, str)

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
            raise PObjectDNE(pobj)
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

    def __init__(self, pbackend, key=None, uid=None, create=False, **kwargs):
        """Initialize Object"""

        #                      create
        # OPEN_EXISTING        False
        # CREATE_OR_OPEN       True

        # Check Args
        if key:
            utility.check_isinstance(key, str)
        if uid:
            utility.check_isinstance(uid, uuid.UUID)

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
        super().__init__(pbackend, key=key, create=create, **kwargs)

        # Save UUID
        self._uid = uid

    @property
    def uid(self):
        return self._uid

class PermissionsObject(PersistentObject):

    def __init__(self, pbackend, key=None, objtype=None, objuid=None, **kwargs):
        """Initialize Object Permissions"""

        # Setup key/objtype/objperm
        if key:
            utility.check_isinstance(key, str)
            parts = key.split(_SEPERATOR)
            if len(parts) == 1:
                objtype = parts[0]
            elif len(parts) == 2:
                objtype = parts[0]
                objuid = uuid.UUID(parts[1])
            else:
                raise ValueError("Could Not Parse Key: {}".format(key))
        else:
            if not objtype:
                raise TypeError("Requires Key or Object Type")
            else:
                utility.check_isinstance(objtype, str)
                key = objtype
                assert(key.count(_SEPERATOR) == 0)
                if objuid:
                    utility.check_isinstance(objuid, uuid.UUID)
                    key += _SEPERATOR + str(objuid)
                    assert(key.count(_SEPERATOR) == 1)

        # Call Parent
        super().__init__(pbackend, key=key, **kwargs)

        # Save Vals
        self._objtype = objtype
        self._objuid = objuid

    @property
    def objtype(self):
        """Return Object Type"""
        return self._objtype

    @property
    def objuid(self):
        """Return Object UID"""
        return self._objuid

class UserDataObject(PersistentObject):

    def __init__(self, pbackend, create=False, userdata={}, **kwargs):
        """Initialize Object"""

        # Check Args
        if create:
            utility.check_isinstance(userdata, dict)

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

    def __init__(self, pbackend, create=False, prefix="srv", **kwargs):

        #                      create
        # OPEN_EXISTING        False
        # CREATE_OR_OPEN       True

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
        utility.check_isinstance(pindex, ChildIndex)
        if pindex.parent.pbackend != pbackend:
            raise TypeError("parent and child must have common pbackend")

        # Call Parent
        super().__init__(pbackend, create=create, **kwargs)

        # Setup Vars
        self._pindex = pindex

        # Register with Index
        # TODO: These operations need to be atomic
        if create:
            if self._pindex.exists(self.key):
                # TODO: Cleanup?
                raise ObjectExists(self)
            self._pindex._children.add(self.key)
        else:
            if not self._pindex.exists(self.key):
                # TODO: Cleanup?
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
        utility.check_isinstance(parent, PersistentObject)
        utility.check_issubclass(type_child, ChildObject)
        utility.check_isinstance(label, str)

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

class MasterObjIndex(object):

    def __init__(self, obj, label, slave_generator, type_member, **extra_kwargs):
        """Initialize Member Index"""

        # Call Parent
        super().__init__()

        # Check Args
        utility.check_isinstance(obj, PersistentObject)
        utility.check_isinstance(label, str)
        if not hasattr(slave_generator, '__call__'):
            raise TypeError("master_generator must be callable")
        utility.check_issubclass(type_member, PersistentObject)

        # Save Args
        self._obj = obj
        self._label = label
        self._slave_generator = slave_generator
        self._type_member = type_member
        self._extra_kwargs = extra_kwargs

        # Setup Index Set
        self._members = self.obj._build_pobj(self.obj.pcollections.MutableSet,
                                             label, create=set())

    def destroy(self):
        """Cleanup Index"""

        for key in self.by_key():
            slv = self._slave_generator(key, **self._extra_kwargs)
            utility.check_isinstance(slv, SlaveObjIndex)
            slv._members.discard(self.obj.key)

        # Cleanup Set
        self._members.rem()

    @property
    def obj(self):
        return self._obj

    @property
    def type_member(self):
        return self._type_member

    def add(self, val):
        key = self.obj.val_to_key(val)
        slv = self._slave_generator(key, **self._extra_kwargs)
        utility.check_isinstance(slv, SlaveObjIndex)
        utility.check_isinstance(slv.obj, self.type_member)
        utility.check_isinstance(self.obj, slv.type_member)
        self._members.add(key)
        slv._members.add(self.obj.key)

    def remove(self, val):
        key = self.obj.val_to_key(val)
        slv = self._slave_generator(key, **self._extra_kwargs)
        utility.check_isinstance(slv, SlaveObjIndex)
        utility.check_isinstance(slv.obj, self.type_member)
        utility.check_isinstance(self.obj, slv.type_member)
        slv._members.discard(self.obj.key)
        self._members.discard(key)

    def __len__(self):
        return len(self._members)

    def ismember(self, val):
        key = self.obj.val_to_key(val)
        return key in self._members

    def by_key(self):
        return self._members.get_val()

    def by_uid(self):
        return set([self.obj.val_to_uid(key)
                    for key in self._members])

    def by_obj(self):
        return set([self.obj.val_to_obj(key, self.type_member, **self._extra_kwargs)
                    for key in self._members])

class SlaveObjIndex(object):

    def __init__(self, obj, label, master_generator, type_member, **extra_kwargs):
        """Initialize Slave Index"""

        # Call Parent
        super().__init__()

        # Check Args
        utility.check_isinstance(obj, PersistentObject)
        utility.check_isinstance(label, str)
        if not hasattr(master_generator, '__call__'):
            raise TypeError("slave_generator must be callable")
        utility.check_issubclass(type_member, PersistentObject)

        # Save Args
        self._obj = obj
        self._label = label
        self._master_generator = master_generator
        self._type_member = type_member
        self._extra_kwargs = extra_kwargs

        # Setup Index Set
        self._members = self.obj._build_pobj(self.obj.pcollections.MutableSet,
                                             label, create=set())

    def destroy(self):
        """Cleanup Index"""

        for key in self.by_key():
            mas = self._master_generator(key, **self._extra_kwargs)
            utility.check_isinstance(mas, MasterObjIndex)
            mas._members.discard(self.obj.key)

        # Cleanup Set
        self._members.rem()

    @property
    def obj(self):
        return self._obj

    @property
    def type_member(self):
        return self._type_member

    def __len__(self):
        return len(self._members)

    def ismember(self, val):
        key = self.obj.val_to_key(val)
        return key in self._members

    def by_key(self):
        return self._members.get_val()

    def by_uid(self):
        return set([self.obj.val_to_uid(key)
                    for key in self._members])

    def by_obj(self):
        return set([self.obj.val_to_obj(key, self.type_member, **self._extra_kwargs)
                    for key in self._members])

class PlainObjIndex(object):

    def __init__(self, obj, label, type_member, init=None, **extra_kwargs):
        """Initialize Member Index"""

        # Call Parent
        super().__init__()

        # Check Args
        utility.check_isinstance(obj, PersistentObject)
        utility.check_isinstance(label, str)
        utility.check_issubclass(type_member, PersistentObject)
        if init:
            utility.check_isinstance(init, set, list)
            init = set(init)
        else:
            init = set()

        # Save Args
        self._obj = obj
        self._label = label
        self._type_member = type_member
        self._extra_kwargs = extra_kwargs

        # Setup Index Set
        self._members = self.obj._build_pobj(self.obj.pcollections.MutableSet,
                                             label, create=init)

    def destroy(self):
        """Cleanup Index"""

        # Cleanup Set
        self._members.rem()

    @property
    def obj(self):
        return self._obj

    @property
    def type_member(self):
        return self._type_member

    def add(self, val):
        key = self.obj.val_to_key(val)
        self._members.add(key)

    def remove(self, val):
        key = self.obj.val_to_key(val)
        self._members.discard(key)

    def __len__(self):
        return len(self._members)

    def ismember(self, val):
        key = self.obj.val_to_key(val)
        return key in self._members

    def by_key(self):
        return self._members.get_val()

    def by_uid(self):
        return set([self.obj.val_to_uid(key)
                    for key in self._members])

    def by_obj(self):
        return set([self.obj.val_to_obj(key, self.type_member, **self._extra_kwargs)
                    for key in self._members])
