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
        self._driver = ds_driver

        # Setup Driver-Bound Factories
        self._org_f_metadata = ds_factories.InstanceFactory(self._driver,
                                                            Organization._type_metadata,
                                                            ds_keys.StrKey)
        self._org_f_accounts = ds_factories.InstanceFactory(self._driver,
                                                            Organization._type_accounts,
                                                            ds_keys.StrKey)

    def organization_from_new(self, name):
        """New Organization Constructor"""

        uid = uuid.uuid4()
        metadata = self._org_f_metadata.from_new(str(uid), {'name': name})
        accounts = self._org_f_accounts.from_new(str(uid), [])
        return Organization(uid, metadata, accounts)

    def organization_from_existing(self, uid):
        """Existing Organization Constructor"""

        uid = uuid.UUID(uid)
        metadata = self._org_f_metadata.from_existing(str(uid))
        accounts = self._org_f_accounts.from_existing(str(uid))
        return Organization(uid, metadata, accounts)

class Organization(object):

    _type_uid = uuid.UUID
    _type_metadata = ds_objects.MutableDictionary
    _type_accounts = ds_objects.MutableList

    def __init__(self, uid, metadata, accounts):

        # Call Parent
        super().__init__()

        # Check Args
        if not isinstance(uid, self._type_uid):
            msg = "'uid' must be of type '{}', ".format(self._type_uid)
            msg += "not '{}'".format(type(uid))
            raise TypeError(msg)
        if not isinstance(metadata, self._type_metadata):
            msg = "'metadata' must be of type '{}', ".format(self._type_metadata)
            msg += "not '{}'".format(type(meta))
            raise TypeError(msg)
        if not isinstance(accounts, self._type_accounts):
            msg = "'accounts' must be of type '{}', ".format(self._type_accounts)
            msg += "not '{}'".format(type(accounts))
            raise TypeError(msg)

        # Save Attrs
        self._uid = uid
        self._metadata = metadata
        self._accounts = accounts

    def rem(self):
        """Delete Organization"""
        self._metadata.rem()
        self._accounts.rem()
