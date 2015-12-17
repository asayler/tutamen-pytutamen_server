# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from pcollections import be_redis_atomic as dso
from pcollections import keys as dsk

from . import datatypes


### Constants ###

_KEY_AUTHORIZATIONS = "authorizations"
_KEY_AUTHENTICATORS = "authenticators"
_KEY_AUTHSETS = "authsets"

_PREFIX_ACCESSCONTROLSERVER = "accesscontrolsrv"
_PREFIX_AUTHORIZATION = "authorization"
_PREFIX_AUTHENTICATOR = "authenticator"
_PREFIX_AUTHSET = "authset"

_POSTFIX_CLIENTUID = "clientuid"
_POSTFIX_EXPIRATION = "expiration"
_POSTFIX_OBJPERM = "objperm"
_POSTFIX_OBJTYPE = "objtype"
_POSTFIX_OBJUID = "objuid"
_POSTFIX_STATUS = "status"
_POSTFIX_MODULE = "module"
_POSTFIX_AUTHSETS = "authsets"
_POSTFIX_AUTHENTICATORS = "authenticators"

_NEW_STATUS = "pending"


### Objects ###

class AccessControlServer(datatypes.PersistentObjectServer):

    def __init__(self, driver, prefix=_PREFIX_ACCESSCONTROLSERVER):

        # Call Parent
        super().__init__(driver, prefix=prefix)

        # Setup Collections Index
        self._authorizations = datatypes.Index(self, key=_KEY_AUTHORIZATIONS, prefix=prefix,
                                               create=True, overwrite=False)
        self._authenticators = datatypes.Index(self, key=_KEY_AUTHENTICATORS, prefix=prefix,
                                               create=True, overwrite=False)
        self._authsets = datatypes.Index(self, key=_KEY_AUTHSETS, prefix=prefix,
                                         create=True, overwrite=False)

    def destroy(self):

        # Cleanup Indexes
        self._authenticators.destroy()
        self._authorizations.destroy()
        self._authsets.destroy()

        # Call Parent
        super().destroy()

    # Authorization Methods #

    def authorizations_create(self, **kwargs):

        return Authorization(self, create=True, **kwargs)

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

    # Authenticator Methods #

    def authenticators_create(self, **kwargs):

        return Authenticator(self, create=True, **kwargs)

    def authenticators_get(self, uid=None, key=None):

        # Check Args
        if not uid and not key:
            raise TypeError("Requires either uid or key")

        # Create
        return Authenticator(self, create=False, key=key, uid=uid)

    def authenticators_list(self):
        return self._authenticators.members

    def authenticators_exists(self, uid=None, key=None):

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
        return self._authenticators.is_member(key)

    # Authset Methods #

    def authsets_create(self, **kwargs):

        return Authset(self, create=True, **kwargs)

    def authsets_get(self, uid=None, key=None):

        # Check Args
        if not uid and not key:
            raise TypeError("Requires either uid or key")

        # Create
        return Authset(self, create=False, key=key, uid=uid)

    def authsets_list(self):
        return self._authsets.members

    def authsets_exists(self, uid=None, key=None):

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
        return self._authsets.is_member(key)

class Authorization(datatypes.UUIDObject, datatypes.UserMetadataObject):

    def __init__(self, srv, create=False, overwrite=False,
                 prefix=_PREFIX_AUTHORIZATION,
                 clientuid=None, expiration=None,
                 objperm=None, objtype=None, objuid=None, **kwargs):
        """Initialize Authorization"""

        # Check Input
        datatypes.check_isinstance(srv, AccessControlServer)
        if create:
            datatypes.check_isinstance(clientuid, uuid.UUID)
            datatypes.check_isinstance(expiration, float)
            datatypes.check_isinstance(objperm, str)
            datatypes.check_isinstance(objtype, str)
            datatypes.check_isinstance(objuid, uuid.UUID)
        if overwrite:
            raise TypeError("Authorization does not support overwrite")

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Setup Status and Token
        self._clientuid = self._build_subobj(dso.String, _POSTFIX_CLIENTUID,
                                             create=create, value=str(clientuid))
        self._expiration = self._build_subobj(dso.String, _POSTFIX_EXPIRATION,
                                              create=create, value=str(expiration))
        self._objperm = self._build_subobj(dso.String, _POSTFIX_OBJPERM,
                                           create=create, value=objperm)
        self._objtype = self._build_subobj(dso.String, _POSTFIX_OBJTYPE,
                                           create=create, value=objtype)
        self._objuid = self._build_subobj(dso.String, _POSTFIX_OBJUID,
                                          create=create, value=str(objuid))
        self._status = self._build_subobj(dso.MutableString, _POSTFIX_STATUS,
                                          create=create, value=_NEW_STATUS)

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
        return uuid.UUID(self._clientuid.get_val())

    @property
    def expiration(self):
        """Return Expiration"""
        return float(self._expiration.get_val())

    @property
    def objperm(self):
        """Return Object Permission"""
        return self._objperm.get_val()

    @property
    def objtype(self):
        """Return Object Type"""
        return self._objtype.get_val()

    @property
    def objuid(self):
        """Return Object UID"""
        return uuid.UUID(self._objuid.get_val())

    @property
    def status(self):
        """Return Status"""
        return self._status.get_val()

class Authenticator(datatypes.UUIDObject, datatypes.UserMetadataObject):

    def __init__(self, srv, create=False, overwrite=False,
                 prefix=_PREFIX_AUTHENTICATOR,
                 module=None, **kwargs):
        """Initialize Authenticator"""

        # Check Input
        datatypes.check_isinstance(srv, AccessControlServer)
        if create:
            datatypes.check_isinstance(module, str)
        if overwrite:
            raise TypeError("Authenticator does not support overwrite")

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Setup Vars
        self._module = self._build_subobj(dso.String, _POSTFIX_MODULE,
                                          create=create, value=module)
        self._authsets = self._build_subobj(dso.MutableSet, _POSTFIX_AUTHSETS,
                                            create=create, value=set())

        # Register with Server
        if create:
            self.srv._authenticators.add(self)
        else:
            if not self.srv.authenticators_exists(key=self.key):
                msg = "Authorization not associated with srv"
                raise TypeError(msg)

    def destroy(self):
        """Delete Authenticator"""

        # Unregister with Server
        self.srv._authenticators.remove(self)

        # Unregister with Authsets
        for authset in self.authsets_by_obj():
            authset.remove(self)

        # Cleanup Vars
        self._authsets.rem()
        self._module.rem()

        # Call Parent
        super().destroy()

    @property
    def module(self):
        """Return Module"""
        return self._module.get_val()

    def authsets_by_key(self):
        """Return Authset Memberships as Keys"""
        return self._authsets.get_val()

    def authsets_by_uid(self):
        """Return Authset Memberships as UUIDs"""
        return set([self._val_to_uid(key) for key in self._authsets])

    def authsets_by_obj(self):
        """Return Authset Memberships as Objects"""
        return set([self._val_to_obj(key, obj=Authset) for key in self._authsets])

class Authset(datatypes.UUIDObject, datatypes.UserMetadataObject):

    def __init__(self, srv, create=False, overwrite=False,
                 prefix=_PREFIX_AUTHSET, **kwargs):
        """Initialize Authset"""

        # Check Input
        datatypes.check_isinstance(srv, AccessControlServer)
        if create:
            pass
        if overwrite:
            raise TypeError("Authenticator does not support overwrite")

        # Call Parent
        super().__init__(srv, create=create, overwrite=overwrite,
                         prefix=prefix, **kwargs)

        # Setup Vars
        self._authenticators = self._build_subobj(dso.MutableSet, _POSTFIX_AUTHENTICATORS,
                                                  create=create, value=set())

        # Register with Server
        if create:
            self.srv._authsets.add(self)
        else:
            if not self.srv.authsets_exists(key=self.key):
                msg = "Authset not associated with srv"
                raise TypeError(msg)

    def destroy(self):
        """Delete Authenticator"""

        # Unregister with Server
        self.srv._authsets.remove(self)

        # Unregister with Authenticators
        for actr in self.members_by_obj():
            self.remove(actr)

        # Cleanup Status and Token
        self._authenticators.rem()

        # Call Parent
        super().destroy()

    def members_by_key(self):
        """Return Authenticator Members as string keys"""
        return self._authenticators.get_val()

    def members_by_uid(self):
        """Return Authenticator Members as UUID objects"""
        return set([self._val_to_uid(key) for key in self._authenticators])

    def members_by_obj(self):
        """Return Authenticator Members as Objects"""
        return set([self._val_to_obj(key, obj=Authenticator) for key in self._authenticators])

    def is_member(self, val):
        """Return if Authenticator is member"""

        # Process Val
        key = self._val_to_key(val)

        # Compute Membership
        return key in self._authenticators

    def add(self, val):
        """Add Authenticator"""

        # Process Val
        actr = self._val_to_obj(val, obj=Authenticator)

        # Add Authenticator
        self._authenticators.add(actr.key)
        actr._authsets.add(self.key)

    def remove(self, val):
        """Remove Authenticator"""

        # Process Val
        actr = self._val_to_obj(val, obj=Authenticator)

        # Remove Authenticator
        actr._authsets.discard(self.key)
        self._authenticators.discard(actr.key)
