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
_INDEX_PREFIX = "master_"
_INDEX_POSTFIX = "_index"


### Exceptions ###

class ObjectDNE(Exception):

    def __init__(self, key):

        # Call Parent
        msg = "Object '{:s}' does not exist".format(key)
        super().__init__(msg)


### Objects ###

class PersistentServer(object, metaclass=abc.ABCMeta):

    def __init__(self, driver):

        # Check Args
        # TODO: Verify driver if of appropriate type

        # Call Parent
        super().__init__()

        # Save Attrs
        self._driver = driver


    def make_factory(self, obj_type, key_type=dsk.StrKey, key_kwargs={}):
        return dsf.Instancefactory(self._driver, obj_type,
                                   key_type=key_type, key_kwargs=key_kwargs)

class PersistentObject(object, metaclass=abc.ABCMeta):

    def __init__(self, srv):
        """Initialize Object"""

        # Check Args
        if not isinstance(srv, PersistentServer):
            msg = "'srv' must be of type '{}', ".format(PersistentServer)
            msg += "not '{}'".format(type(srv))
            raise TypeError(msg)

        # Call Parent
        super().__init__()

        # Save Attrs
        self._srv = srv


class IndexedObject(PersistentObject):

    def __init__(self, *args, indexes=[], **kwargs):
        """Initialize Object"""

        # Call Parent
        super().__init__(*args, **kwargs)

        # Create Index Factory
        index_fac = self._srv.make_factory(dso.MutableSet, key_type=dsk.StrKey)
        index_key = _INDEX_PREFIX + type(self).__name__.lower() + _INDEX_POSTFIX
        obj_index = index_factory.from_raw(index_key)
        if not obj_index.exists():
            obj_index.create(set())

        # Save Attrs
        indexes.append(obj_index)
        self._indexes = indexes

    def _register(self):
        pass

    def _unregister(self):
        pass

    @classmethod
    def instance_list():
        pass

    @classmethod
    def instance_exists():
        pass
