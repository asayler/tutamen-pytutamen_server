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
        self._authenticators = self._build_pobj(self.pcollections.MutableSet,
                                                _POSTFIX_AUTHENTICATORS,
                                                create=set())
        self._accounts = self._build_pobj(self.pcollections.MutableSet,
                                          _POSTFIX_ACCOUNTS,
                                          create=set())

    def destroy(self):
        """Delete Authenticator"""

        # Unregister with Authenticators
        for actr in self.authenticators_by_obj():
            self.authenticators_remove(actr)

        # Unregister with Accounts
        for acct in self.accounts_by_obj():
            self.accounts_remove(acct)

        # Cleanup Status and Token
        self._accounts.rem()
        self._authenticators.rem()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.parent

    # Authenticator Methods #

    def authenticators_by_key(self):
        """Return Authenticators as key strings"""
        return self._authenticators.get_val()

    def authenticators_by_uid(self):
        """Return Authenticators as UUID objects"""
        return set([self.srv.val_to_uid(key) for key in self._authenticators])

    def authenticators_by_obj(self):
        """Return Authenticators as objects"""
        return set([self.srv.val_to_obj(key, Authenticator) for key in self._authenticators])

    def authenticators_is_member(self, val):
        """Return if Authenticator is member"""

        # Process Val
        key = self.srv.val_to_key(val)

        # Compute Membership
        return key in self._authenticators

    def authenticators_add(self, val):
        """Add Authenticator"""

        # Process Val
        actr = self.srv.val_to_obj(val, Authenticator)

        # Add Authenticator
        self._authenticators.add(actr.key)
        actr._verifiers.add(self.key)

    def authenticators_remove(self, val):
        """Remove Authenticator"""

        # Process Val
        actr = self.srv.val_to_obj(val, Authenticator)

        # Remove Authenticator
        actr._verifiers.discard(self.key)
        self._authenticators.discard(actr.key)

    # Account Methods #

    def accounts_by_key(self):
        """Return Accounts as key strings"""
        return self._accounts.get_val()

    def accounts_by_uid(self):
        """Return Accounts as UUID objects"""
        return set([self.srv.val_to_uid(key) for key in self._accounts])

    def accounts_by_obj(self):
        """Return Accounts as objects"""
        return set([self.srv.val_to_obj(key, Account) for key in self._accounts])

    def accounts_is_member(self, val):
        """Return if Account is member"""

        # Process Val
        key = self.srv.val_to_key(val)

        # Compute Membership
        return key in self._accounts

    def accounts_add(self, val):
        """Add Account"""

        # Process Val
        acct = self.srv.val_to_obj(val, Account)

        # Add Account
        self._accounts.add(acct.key)
        acct._verifiers.add(self.key)

    def accounts_remove(self, val):
        """Remove Account"""

        # Process Val
        acct = self.srv.val_to_obj(val, Account)

        # Remove Account
        acct._verifiers.discard(self.key)
        self._accounts.discard(acct.key)

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
        self._module = self._build_pobj(self.pcollections.String,
                                        _POSTFIX_MODULE,
                                        create=module)
        self._verifiers = self._build_pobj(self.pcollections.MutableSet,
                                           _POSTFIX_VERIFIERS,
                                           create=set())

    def destroy(self):
        """Delete Authenticator"""

        # Unregister with Verifiers
        for verifier in self.verifiers_by_obj():
            verifier.authenticators_remove(self)

        # Cleanup Vars
        self._verifiers.rem()
        self._module.rem()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Storage Server"""
        return self.parent

    @property
    def module(self):
        """Return Module"""
        return self._module.get_val()

    def verifiers_by_key(self):
        """Return Verifier Memberships as Keys"""
        return self._verifiers.get_val()

    def verifiers_by_uid(self):
        """Return Verifier Memberships as UUIDs"""
        return set([self.srv.val_to_uid(key) for key in self._verifiers])

    def verifiers_by_obj(self):
        """Return Verifier Memberships as Objects"""
        return set([self.srv.val_to_obj(key, Verifier) for key in self._verifiers])

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
        self._verifiers = self._build_pobj(self.pcollections.MutableSet,
                                           _POSTFIX_VERIFIERS,
                                           create=set())
        self._clients = datatypes.ChildIndex(self, Client, _POSTFIX_CLIENTS)

    def destroy(self):
        """Delete Account"""

        # Unregister with Verifiers
        for verifier in self.verifiers_by_obj():
            verifier.accounts_remove(self)

        # Cleanup Vars
        self._clients.destroy()
        self._verifiers.rem()

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

    def verifiers_by_key(self):
        """Return Verifier Memberships as Keys"""
        return self._verifiers.get_val()

    def verifiers_by_uid(self):
        """Return Verifier Memberships as UUIDs"""
        return set([self.srv.val_to_uid(key) for key in self._verifiers])

    def verifiers_by_obj(self):
        """Return Verifier Memberships as Objects"""
        return set([self.srv.val_to_obj(key, Verifier) for key in self._verifiers])

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
