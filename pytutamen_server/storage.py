# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid
import urllib.parse


from . import utility
from . import datatypes


### Constants ###

_INDEX_KEY_SECRETS = "secrets"
_INDEX_KEY_COLLECTIONS = "collections"

_KEY_STORAGESRV = "storage"

_PREFIX_COLLECTION = "collection"
_PREFIX_SECRET = "secret"

_POSTFIX_DATA = "data"
_POSTFIX_ACSERVERS = "acservers"
_POSTFIX_ACREQUIRED = "acrequired"


### Objects ###

class StorageServer(datatypes.ServerObject):

    def __init__(self, pbackend, key=_KEY_STORAGESRV, create=False):

        # Call Parent
        super().__init__(pbackend, key=key, create=create)

        # Setup Collections Index
        self._collections = datatypes.ChildIndex(self, Collection, _INDEX_KEY_SECRETS)

    def destroy(self):

        # Cleanup Indexes
        self._collections.destroy()

        # Call Parent
        super().destroy()

    @property
    def collections(self):
        return self._collections

class Collection(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, prefix=_PREFIX_COLLECTION, 
                 ac_servers=None, ac_required=None, create=False, **kwargs):
        """Initialize Collection"""

        # Check Input
        utility.check_isinstance(pindex.parent, StorageServer)
        if create:
            utility.check_isinstance(ac_servers, list)
            utility.check_isinstance(ac_required, int)

            urls = []
            for url in ac_servers:
                # Todo: normalize URL
                p = urllib.parse.urlparse(url)
                if not p.scheme.lower() == 'https':
                    raise ValueError("AC URL requires https")
                if not p.hostname:
                    raise ValueError("AC URL requires hostname")
                if p.path:
                    raise ValueError("AC URL should have no path")

        # Call Parent
        super().__init__(pbackend, pindex=pindex, prefix=prefix, create=create, **kwargs)

        # Setup Objects
        self._ac_servers = self._build_pobj(self.pcollections.MutableList,
                                            _POSTFIX_ACSERVERS, create=ac_servers)
        self._ac_required = self._build_pobj(self.pcollections.MutableString,
                                             _POSTFIX_ACREQUIRED, create=str(ac_required))

        # Setup Secret Index
        self._secrets = datatypes.ChildIndex(self, Secret, _INDEX_KEY_SECRETS)

    def destroy(self):
        """Delete Collection"""

        # Cleanup Indexes
        self._secrets.destroy()

        # Cleanup Objects
        self._ac_required.rem()
        self._ac_servers.rem()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.parent

    @property
    def ac_servers(self):
        return self._ac_servers.get_val()

    @property
    def ac_required(self):
        return int(self._ac_required.get_val())

    @property
    def secrets(self):
        return self._secrets

class Secret(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False, prefix=_PREFIX_SECRET,
                 data="", **kwargs):
        """Initialize Secret"""

        # Check Input
        utility.check_isinstance(pindex.parent, Collection)
        if create:
            utility.check_isinstance(data, str)

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Data
        self._data = self._build_pobj(self.pcollections.String, _POSTFIX_DATA, create=data)

    def destroy(self):
        """Delete Secret"""

        # Cleanup Objects
        self._data.rem()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.collection.server

    @property
    def collection(self):
        """Return Collection"""
        return self.parent

    @property
    def data(self):
        """Return Secret Data"""
        return self._data.get_val()
