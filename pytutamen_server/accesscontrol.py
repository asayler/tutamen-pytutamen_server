# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import uuid

from . import datatypes


### Constants ###

_KEY_AUTHORIZATIONS = "authorizations"
_KEY_VERIFIERS = "verifiers"
_KEY_AUTHENTICATORS = "authenticators"
_KEY_ACCOUNTS = "accounts"

_KEY_ACSRV = "accesscontrol"

_PREFIX_AUTHORIZATION = "authorization"
_PREFIX_VERIFIER = "verifier"
_PREFIX_AUTHENTICATOR = "authenticator"
_PREFIX_ACCOUNT = "account"
_PREFIX_CLIENT = "client"

_POSTFIX_CLIENTUID = "clientuid"
_POSTFIX_EXPIRATION = "expiration"
_POSTFIX_OBJPERM = "objperm"
_POSTFIX_OBJTYPE = "objtype"
_POSTFIX_OBJUID = "objuid"
_POSTFIX_STATUS = "status"
_POSTFIX_MODULE = "module"
_POSTFIX_VERIFIERS = "verifiers"
_POSTFIX_AUTHENTICATORS = "authenticators"
_POSTFIX_ACCOUNTS = "accounts"
_POSTFIX_CLIENTS = "clients"

_NEW_STATUS = "pending"


### Objects ###

class AccessControlServer(datatypes.ServerObject):

    def __init__(self, pbackend, key=_KEY_ACSRV):

        # Call Parent
        super().__init__(pbackend, key=key)

        # Setup Collections Index
        self._authorizations = datatypes.ChildIndex(self, Authorization, _KEY_AUTHORIZATIONS)
        self._verifiers = datatypes.ChildIndex(self, Verifier, _KEY_VERIFIERS)
        self._authenticators = datatypes.ChildIndex(self, Authenticator, _KEY_AUTHENTICATORS)
        self._accounts = datatypes.ChildIndex(self, Account, _KEY_ACCOUNTS)

    def destroy(self):

        # Cleanup Indexes
        self._accounts.destroy()
        self._authenticators.destroy()
        self._verifiers.destroy()
        self._authorizations.destroy()

        # Call Parent
        super().destroy()

    @property
    def authorizations(self):
        return self._authorizations

    @property
    def verifiers(self):
        return self._verifiers

    @property
    def authenticators(self):
        return self._authenticators

    @property
    def accounts(self):
        return self._accounts

class Authorization(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_AUTHORIZATION,
                 clientuid=None, expiration=None,
                 objperm=None, objtype=None, objuid=None, **kwargs):
        """Initialize Authorization"""

        # Check Input
        datatypes.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            datatypes.check_isinstance(clientuid, uuid.UUID)
            datatypes.check_isinstance(expiration, float)
            datatypes.check_isinstance(objperm, str)
            datatypes.check_isinstance(objtype, str)
            datatypes.check_isinstance(objuid, uuid.UUID)

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Data
        self._clientuid = self._build_pobj(self.pcollections.String,
                                           _POSTFIX_CLIENTUID,
                                           create=datatypes.nos(clientuid))
        self._expiration = self._build_pobj(self.pcollections.String,
                                            _POSTFIX_EXPIRATION,
                                            create=datatypes.nos(expiration))
        self._objperm = self._build_pobj(self.pcollections.String,
                                         _POSTFIX_OBJPERM,
                                         create=objperm)
        self._objtype = self._build_pobj(self.pcollections.String,
                                         _POSTFIX_OBJTYPE,
                                         create=objtype)
        self._objuid = self._build_pobj(self.pcollections.String,
                                        _POSTFIX_OBJUID,
                                        create=datatypes.nos(objuid))
        self._status = self._build_pobj(self.pcollections.MutableString,
                                        _POSTFIX_STATUS,
                                        create=_NEW_STATUS)

    def destroy(self):
        """Delete Authorization"""

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
    def server(self):
        """Return Storage Server"""
        return self.parent

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

class Verifier(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_VERIFIER, **kwargs):
        """Initialize Verifier"""

        # Check Input
        datatypes.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            pass

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Vars
        def authenticator_masters(key, **kwargs):
            return Authenticator(self.pbackend, key=key, **kwargs).verifiers
        self._authenticators = datatypes.MasterObjIndex(self, _POSTFIX_AUTHENTICATORS,
                                                        authenticator_masters,
                                                        Authenticator,
                                                        pindex=self.server.authenticators)
        def account_masters(key, **kwargs):
            return Account(self.pbackend, key=key, **kwargs).verifiers
        self._accounts = datatypes.MasterObjIndex(self, _POSTFIX_ACCOUNTS,
                                                  account_masters,
                                                  Account,
                                                  pindex=self.server.accounts)

    def destroy(self):
        """Delete Verifier"""

        # Cleanup Indexes
        self._accounts.destroy()
        self._authenticators.destroy()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.parent

    @property
    def authenticators(self):
        """Return Authenticators Object Index"""
        return self._authenticators

    @property
    def accounts(self):
        """Return Accounts Object Index"""
        return self._accounts

class Authenticator(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_AUTHENTICATOR,
                 module=None, **kwargs):
        """Initialize Authenticator"""

        # Check Input
        datatypes.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            datatypes.check_isinstance(module, str)

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Vars
        def verifier_slaves(key, **kwargs):
            return Verifier(self.pbackend, key=key, **kwargs).authenticators
        self._verifiers = datatypes.SlaveObjIndex(self, _POSTFIX_VERIFIERS,
                                                  verifier_slaves,
                                                  Verifier,
                                                  pindex=self.server.verifiers)
        self._module = self._build_pobj(self.pcollections.String,
                                        _POSTFIX_MODULE,
                                        create=module)

    def destroy(self):
        """Delete Authenticator"""

        # Cleanup Vars
        self._module.rem()
        self._verifiers.destroy()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.parent

    @property
    def verifiers(self):
        """Return Verifiers Object Index"""
        return self._verifiers

    @property
    def module(self):
        """Return Module"""
        return self._module.get_val()

class Account(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_ACCOUNT, **kwargs):
        """Initialize Account"""

        # Check Input
        datatypes.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            pass

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Vars
        self._clients = datatypes.ChildIndex(self, Client, _POSTFIX_CLIENTS)
        def verifier_slaves(key, **kwargs):
            return Verifier(self.pbackend, key=key, **kwargs).accounts
        self._verifiers = datatypes.SlaveObjIndex(self, _POSTFIX_VERIFIERS,
                                                  verifier_slaves,
                                                  Verifier,
                                                  pindex=self.server.verifiers)

    def destroy(self):
        """Delete Account"""

        # Cleanup Indexes
        self._verifiers.destroy()
        self._clients.destroy()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.parent

    @property
    def clients(self):
        """Return Client Index"""
        return self._clients

    @property
    def verifiers(self):
        """Return Verifiers Object Index"""
        return self._verifiers

class Client(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_CLIENT, **kwargs):
        """Initialize Client"""

        # Check Input
        datatypes.check_isinstance(pindex.parent, Account)
        if create:
            pass

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

    def destroy(self):
        """Delete Account"""

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.account.server

    @property
    def account(self):
        """Return Account"""
        return self.parent
