# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as dso
from pcollections import keys as dsk

from . import datatypes


### Constants ###

_INDEX_KEY_AUTHORIZATIONS = "authorizations"

_PREFIX_ACCESSCONTROLSERVER = "accesscontrolsrv"

_PREFIX_AUTHORIZATION = "authorization"

_POSTFIX_CLIENTUID = "clientuid"
_POSTFIX_EXPIRATION = "expiration"
_POSTFIX_OBJPERM = "objperm"
_POSTFIX_OBJTYPE = "objtype"
_POSTFIX_OBJUID = "objuid"
_POSTFIX_STATUS = "status"

_NEW_STATUS = "pending"


### Objects ###

class AccessControlServer(datatypes.PersistentObjectServer):

    def __init__(self, driver, prefix=_PREFIX_ACCESSCONTROLSERVER):

        # Call Parent
        super().__init__(driver, prefix=prefix)

        # Setup Collections Index
        key = _INDEX_KEY_AUTHORIZATIONS
        self._authorizations = datatypes.Index(self, key=key, prefix=prefix,
                                               create=True, overwrite=False)

    def destroy(self):

        # Cleanup Indexes
        self._authorizations.destroy()

        # Call Parent
        super().destroy()

    def authorizations_create(self, clientuid=None, expiration=None,
                              objperm=None, objtype=None, objuid=None,
                              usermetadata={}):

        return Authorization(self, create=True, clientuid=clientuid, expiration=expiration,
                             objperm=objperm, objtype=objtype, objuid=objuid,
                             usermetadata=usermetadata)

    def authorizations_get(self, uid=None, key=None):

        # Check Args
        if not uid and not key:
            raise TypeError("Requires either uid or key")

        # Create
        return Authorization(self, create=False, key=key, uid=uid)

    def authorizations_list(self):
        return self._authorizations.members

    def authorizations_exists(self, uid=None, key=None):

        # Check Args
        if not uid and not key:
            raise TypeError("Requires either uid or key")
        if uid:
            datatypes.check_isinstance(uid, uuid.UUID)
        if key:
            datatypes.check_isinstance(key, str)

        # Convert key
        if not key:
            key = str(uid)

        # Check membership
        return self._authorizations.is_member(key)

class Authorization(datatypes.UUIDObject, datatypes.UserMetadataObject):

    def __init__(self, srv, create=False, overwrite=False,
                 prefix=_PREFIX_AUTHORIZATION,
                 clientuid=None, expiration=None,
                 objperm=None, objtype=None, objuid=None, **kwargs):
        """Initialize Authorization"""

        # Check Input
        datatypes.check_isinstance(srv, AuthorizationServer)
        if create:
            pass
        if overwrite:
            raise TypeError("Authorization does not support overwrite")

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Setup Status and Token
        factory = self.srv.make_factory(dso.String, key_type=dsk.StrKey)
        key = self._build_key(_POSTFIX_CLIENTUID)
        self._clientuid = factory.from_raw(key)
        if not self._clientuid.exists():
            if create:
                self._clientuid.create(client)
            else:
                raise ObjectDNE(self)
        factory = self.srv.make_factory(dso.String, key_type=dsk.StrKey)
        key = self._build_key(_POSTFIX_EXPIRATION)
        self._expiration = factory.from_raw(key)
        if not self._expiration.exists():
            if create:
                self._expiration.create(expiration)
            else:
                raise ObjectDNE(self)
        factory = self.srv.make_factory(dso.String, key_type=dsk.StrKey)
        key = self._build_key(_POSTFIX_OBJPERM)
        self._objperm = factory.from_raw(key)
        if not self._objperm.exists():
            if create:
                self._objperm.create(permission)
            else:
                raise ObjectDNE(self)
        factory = self.srv.make_factory(dso.String, key_type=dsk.StrKey)
        key = self._build_key(_POSTFIX_OBJTYPE)
        self._objtype = factory.from_raw(key)
        if not self._objtype.exists():
            if create:
                self._objtype.create(objtype)
            else:
                raise ObjectDNE(self)
        factory = self.srv.make_factory(dso.String, key_type=dsk.StrKey)
        key = self._build_key(_POSTFIX_OBJUID)
        self._objuid = factory.from_raw(key)
        if not self._objuid.exists():
            if create:
                self._objuid.create(objuid)
            else:
                raise ObjectDNE(self)
        factory = self.srv.make_factory(dso.MutableString, key_type=dsk.StrKey)
        key = self._build_key(_POSTFIX_STATUS)
        self._status = factory.from_raw(key)
        if not self._status.exists():
            if create:
                self._status.create(_NEW_STATUS)
            else:
                raise ObjectDNE(self)

        # Register with Server
        if create:
            self.srv._authorizations.add(self)
        else:
            if not self.srv.authorizations_exists(key=self.key):
                msg = "Authorization not associated with srv"
                raise TypeError(msg)

    def destroy(self):
        """Delete Authorization"""

        # Unregister with Server
        self.srv._authorizations.remove(self)

        # Cleanup Status and Token
        self._clientuid.rem()
        self._expiration.rem()
        self._objperm.rem()
        self._objtype.rem()
        self._objuid.rem()
        self._status.rem()

        # Call Parent
        super().destroy()

    @property
    def clientuid(self):
        """Return Client UID"""
        return self._clientuid

    @property
    def expiration(self):
        """Return Expiration"""
        return self._expiration

    @property
    def objperm(self):
        """Return Object Permission"""
        return self._objperm

    @property
    def objtype(self):
        """Return Object Type"""
        return self._objtype

    @property
    def objuid(self):
        """Return Object UID"""
        return self._objuid

    @property
    def status(self):
        """Return Status"""
        return self._status
