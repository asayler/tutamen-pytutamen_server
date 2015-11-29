# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as ds_objects
from pcollections import factories as ds_factories
from pcollections import keys as ds_keys


### Objects ###

class ManagmentServer(object):

    def __init__(self, ds_driver):

        # Call Parent
        super().__init__()

        # Save Attrs
        self._ds_driver = ds_driver


    def organization_new(self, name):
        return Organization.from_new(self._ds_driver, name)
    def organization_existing(self, uid):
        return Organization.from_existing(self._ds_driver, uid)

class Organization(object):

    def __init__(self, driver, uid, meta, accounts):

        # Call Parent
        super().__init__()

        # Check Args
        if not isinstance(uid, uuid.UUID):
            msg = "'uid' must be of type '{}', ".format(uuid.UUID)
            msg += "not '{}'".format(type(uid))
            raise TypeError(msg)
        if not isinstance(meta, ds_objects.MutableDictionary):
            msg = "'meta' must be of type '{}', ".format(ds_objects.MutableDictionary)
            msg += "not '{}'".format(type(meta))
            raise TypeError(msg)
        if not isinstance(accounts, ds_objects.MutableList):
            msg = "'accounts' must be of type '{}', ".format(ds_objects.MutableDictionary)
            msg += "not '{}'".format(type(accounts))
            raise TypeError(msg)

        # Save Attrs
        self._ds_driver = driver
        self._uuid = uuid
        self._meta = meta
        self._accounts = accounts

    @classmethod
    def from_new(cls, driver, name):
        """New Constructor"""

        meta_f = ds_factories.InstanceFactory(driver, ds_objects.MutableDictionary, ds_keys.StrKey)
        accounts_f = ds_factories.InstanceFactory(driver, ds_objects.MutableList, ds_keys.StrKey)
        uid = uuid.uuid4()
        d = {'name': name}
        meta = meta_f.from_new(str(uid), d)
        l = []
        accounts = accounts_f.from_new(str(uid), l)

        return cls(driver, uid, meta, accounts)

    @classmethod
    def from_existing(cls, driver, uid):
        """Existing Constructor"""

        meta_f = ds_factories.InstanceFactory(driver, ds_objects.MutableDictionary, ds_keys.StrKey)
        accounts_f = ds_factories.InstanceFactory(driver, ds_objects.MutableList, ds_keys.StrKey)
        uid = uuid.UUID(uid)
        meta = meta_f.from_existing(str(uid))
        accounts = accounts_f.from_existing(str(uid))

        return cls(driver, uid, meta, accounts)

    def rem(self):
        """Delete Organization"""
        self._meta.rem()
        self._accounts.rem()
