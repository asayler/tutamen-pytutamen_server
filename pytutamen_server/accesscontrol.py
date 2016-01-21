# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import datetime
import uuid

from . import crypto
from . import utility
from . import constants
from . import datatypes

### Constants ###

_PERM_SEPERATOR = "_"

_KEY_AUTHORIZATIONS = "authorizations"
_KEY_VERIFIERS = "verifiers"
_KEY_AUTHENTICATORS = "authenticators"
_KEY_ACCOUNTS = "accounts"
_KEY_COLLECTION_PERMS = "collection_perms"

_KEY_ACSRV = "accesscontrol"

_PREFIX_AUTHORIZATION = "authorization"
_PREFIX_VERIFIER = "verifier"
_PREFIX_AUTHENTICATOR = "authenticator"
_PREFIX_ACCOUNT = "account"
_PREFIX_CLIENT = "client"

_POSTFIX_CA_CRT = "ca_crt"
_POSTFIX_CA_KEY = "ca_key"
_POSTFIX_SIGKEY_PUB = "sigkey_pub"
_POSTFIX_SIGKEY_PRIV = "sigkey_priv"
_POSTFIX_CLIENT_CRT = "crt"

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

_PREFIX_PERM = "permissions"

AUTHZ_STATUS_NEW = "pending"
AUTHZ_STATUS_APPROVED = "approved"
AUTHZ_STATUS_DENIED = "denied"


### Exceptions ###

class AuthorizationException(Exception):

    pass

class AuthorizationNotApproved(AuthorizationException):

    def __init__(self, authz):

        # Check Args
        utility.check_isinstance(authz, Authorization)

        # Message
        msg = "Authorization {} not approved".format(authz.key)

        # Call Parent
        super().__init__(msg)


### Objects ###

class AccessControlServer(datatypes.ServerObject):

    def __init__(self, pbackend, key=_KEY_ACSRV, create=False,
                 ca_crt_pem=None, ca_key_pem=None,
                 sigkey_pub_pem=None, sigkey_priv_pem=None,
                 cn=None, country=None, state=None, locality=None,
                 organization=None, ou=None, email=None):

        # Call Parent
        super().__init__(pbackend, key=key, create=create)

        # Setup Collections Index
        self._authorizations = datatypes.ChildIndex(self, Authorization, _KEY_AUTHORIZATIONS)
        self._verifiers = datatypes.ChildIndex(self, Verifier, _KEY_VERIFIERS)
        self._authenticators = datatypes.ChildIndex(self, Authenticator, _KEY_AUTHENTICATORS)
        self._accounts = datatypes.ChildIndex(self, Account, _KEY_ACCOUNTS)
        self._collection_perms = datatypes.ChildIndex(self, CollectionPerms, _KEY_COLLECTION_PERMS)

        # Setup CA Keys
        if create:
            if ca_crt_pem:
                if ca_key_pem:
                    utility.check_isinstance(ca_crt_pem, str, bytes)
                    utility.check_isinstance(ca_key_pem, str, bytes)
                else:
                    raise TypeError("Providing ca_crt_pem requires providing ca_key_pem")
            else:
                utility.check_isinstance(cn, str)
                utility.check_isinstance(country, str)
                utility.check_isinstance(state, str)
                utility.check_isinstance(locality, str)
                utility.check_isinstance(organization, str)
                utility.check_isinstance(ou, str)
                utility.check_isinstance(email, str)
                ca_crt_pem, ca_key_pem = crypto.gen_ca_pair(cn, country, state, locality,
                                                            organization, ou, email,
                                                            ca_key_pem=ca_key_pem)
        self._ca_crt = self._build_pobj(self.pcollections.String,
                                        _POSTFIX_CA_CRT,
                                        create=ca_crt_pem)
        self._ca_key = self._build_pobj(self.pcollections.String,
                                        _POSTFIX_CA_KEY,
                                        create=ca_key_pem)

        # Setup Sig Keys
        if create:
            if sigkey_pub_pem:
                if sigkey_priv_pem:
                    utility.check_isinstance(sigkey_pub_pem, str, bytes)
                    utility.check_isinstance(sigkey_priv_pem, str, bytes)
                else:
                    raise TypeError("Providing sigkey_pub_pem requires providing sigkey_priv_pem")
            else:
                sigkey_pub_pem, sigkey_priv_pem = crypto.gen_key_pair(length=4096,
                                                                      priv_key_pem=sigkey_priv_pem)
        self._sigkey_pub = self._build_pobj(self.pcollections.String,
                                             _POSTFIX_SIGKEY_PUB,
                                             create=sigkey_pub_pem)
        self._sigkey_priv = self._build_pobj(self.pcollections.String,
                                              _POSTFIX_SIGKEY_PRIV,
                                              create=sigkey_priv_pem)

    def destroy(self):

        # Cleanup Objects
        self._sigkey_priv.rem()
        self._sigkey_pub.rem()
        self._ca_key.rem()
        self._ca_crt.rem()

        # Cleanup Indexes
        self._collection_perms.destroy()
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

    @property
    def collection_perms(self):
        return self._collection_perms

    @property
    def ca_crt(self):
        return self._ca_crt.get_val()

    @property
    def ca_key(self):
        return self._ca_key.get_val()

    @property
    def sigkey_pub(self):
        return self._sigkey_pub.get_val()

    @property
    def sigkey_priv(self):
        return self._sigkey_priv.get_val()

class Authorization(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_AUTHORIZATION,
                 clientuid=None, expiration=None,
                 objperm=None, objtype=None, objuid=None, **kwargs):
        """Initialize Authorization"""

        # Check Input
        utility.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            utility.check_isinstance(clientuid, uuid.UUID)
            clientuid = str(clientuid)
            utility.check_isinstance(expiration, datetime.datetime)
            expiration = str(int(expiration.timestamp()))
            utility.check_isinstance(objperm, str)
            utility.check_isinstance(objtype, str)
            if objuid:
                utility.check_isinstance(objuid, uuid.UUID)
                objuid = str(objuid)
            else:
                objuid = ""
        else:
            clientuid = None
            expiration = None
            objperm = None
            objtype = None
            objuid = None

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Data
        self._clientuid = self._build_pobj(self.pcollections.String,
                                           _POSTFIX_CLIENTUID,
                                           create=clientuid)
        self._expiration = self._build_pobj(self.pcollections.String,
                                            _POSTFIX_EXPIRATION,
                                            create=expiration)
        self._objperm = self._build_pobj(self.pcollections.String,
                                         _POSTFIX_OBJPERM,
                                         create=objperm)
        self._objtype = self._build_pobj(self.pcollections.String,
                                         _POSTFIX_OBJTYPE,
                                         create=objtype)
        self._objuid = self._build_pobj(self.pcollections.String,
                                        _POSTFIX_OBJUID,
                                        create=objuid)
        self._status = self._build_pobj(self.pcollections.MutableString,
                                        _POSTFIX_STATUS,
                                        create=AUTHZ_STATUS_NEW)

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
        """Return Access Control Server"""
        return self.parent

    @property
    def clientuid(self):
        """Return Client UID"""
        return uuid.UUID(self._clientuid.get_val())

    @property
    def expiration(self):
        """Return Expiration"""
        return datetime.datetime.fromtimestamp(self.expiration_timestamp)

    @property
    def expiration_timestamp(self):
        """Return Expiration Timestamp"""
        return int(self._expiration.get_val())

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
        objuid = self._objuid.get_val()
        return uuid.UUID(objuid) if objuid else None

    @property
    def status(self):
        """Return Status"""
        return self._status.get_val()

    def verify(self):
        """Verify Authorization Request"""

        # Todo: actually verify authorization against permissions
        self._status.set_val(AUTHZ_STATUS_APPROVED)
        return True

    def export_token(self):
        """Get signed assertion token"""

        if self.status != AUTHZ_STATUS_APPROVED:
            raise AuthorizationNotApproved(self)

        token = utility.encode_auth_token(self.server.sigkey_priv,
                                          self.clientuid,
                                          self.expiration,
                                          self.objperm,
                                          self.objtype,
                                          self.objuid)

        # Assertion Check
        val = utility.decode_auth_token(self.server.sigkey_pub, token)
        assert(val[utility.AUTHZ_KEY_CLIENTUID] == self.clientuid)
        assert(val[utility.AUTHZ_KEY_EXPIRATION] == self.expiration)
        assert(val[utility.AUTHZ_KEY_OBJPERM] == self.objperm)
        assert(val[utility.AUTHZ_KEY_OBJTYPE] == self.objtype)
        assert(val[utility.AUTHZ_KEY_OBJUID] == self.objuid)

        return token

class Verifier(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_VERIFIER,
                 accounts=None, authenticators=None, **kwargs):
        """Initialize Verifier"""

        # Check Input
        utility.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            pass
        if accounts is None:
            accounts = []
        if authenticators is None:
            authenticators = []

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

        # Add initial values:
        for account in accounts:
            self.accounts.add(account)
        for authenticator in authenticators:
            self.autenticators.add(authenticator)

    def destroy(self):
        """Delete Verifier"""

        # Cleanup Indexes
        self._accounts.destroy()
        self._authenticators.destroy()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Access Control Server"""
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
        utility.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            utility.check_isinstance(module, str)

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
        """Return Access Control Server"""
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
        utility.check_isinstance(pindex.parent, AccessControlServer)
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
        """Return Access Control Server"""
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
                 prefix=_PREFIX_CLIENT, csr_pem=None, **kwargs):
        """Initialize Client"""

        # Check Input
        utility.check_isinstance(pindex.parent, Account)
        if create:
            utility.check_isinstance(csr_pem, str, bytes)

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Client Cert
        if create:
            crt_pem = crypto.csr_to_crt(csr_pem, self.server.ca_crt, self.server.ca_key,
                                        cn=self.key, serial=self.uid)
        else:
            crt_pem = None
        self._crt = self._build_pobj(self.pcollections.String,
                                     _POSTFIX_CLIENT_CRT,
                                     create=crt_pem)

    def destroy(self):
        """Delete Account"""

        # Cleanup Objects
        self._crt.rem()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Access Control Server"""
        return self.account.server

    @property
    def account(self):
        """Return Account"""
        return self.parent

    @property
    def crt(self):
        """Return Certificate"""
        return self._crt.get_val()

class CollectionPerms(datatypes.PermissionsObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 verifiers_create=None, verifiers_read=None,
                 verifiers_modify=None, verifiers_delete=None,
                 verifiers_ac=None, verifiers_default=None,
                 **kwargs):
        """Initialize Account"""

        # Check Input
        utility.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            pass
        if verifiers_default is not None:
            if verifers_create is None:
                verifiers_create = verifiers_default
            if verifers_read is None:
                verifiers_read = verifiers_default
            if verifers_modify is None:
                verifiers_modify = verifiers_default
            if verifers_delete is None:
                verifiers_delete = verifiers_default
            if verifers_ac is None:
                verifiers_ac = verifiers_default

        # Call Parent
        prefix = _PREFIX_PERM + _PERM_SEPERATOR + constants.TYPE_COL
        super().__init__(pbackend, pindex=pindex, create=create,
                         prefix=prefix,
                         objtype=constants.TYPE_COL, **kwargs)

        if not self.objuid:
            raise TypeError("Requires objuid")

        # Setup Vars
        create_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_CREATE
        self._perm_create = datatypes.PlainObjIndex(self, create_label, Verifier,
                                                    init=verifiers_create)
        read_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_READ
        self._perm_read = datatypes.PlainObjIndex(self, read_label, Verifier,
                                                  init=verifiers_read)
        modify_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_MODIFY
        self._perm_modify = datatypes.PlainObjIndex(self, modify_label, Verifier,
                                                    init=verifiers_modify)
        delete_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_DELETE
        self._perm_delete = datatypes.PlainObjIndex(self, delete_label, Verifier,
                                                    init=verifiers_delete)
        ac_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_AC
        self._perm_ac = datatypes.PlainObjIndex(self, ac_label, Verifier,
                                                init=verifiers_ac)

    def destroy(self):
        """Delete Account"""

        # Cleanup Indexes
        self._perm_ac.destroy()
        self._perm_delete.destroy()
        self._perm_modify.destroy()
        self._perm_read.destroy()
        self._perm_create.destroy()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Access Control Server"""
        return self.parent

    @property
    def perm_create(self):
        return self._perm_create

    @property
    def perm_read(self):
        return self._perm_read

    @property
    def perm_modify(self):
        return self._perm_modify

    @property
    def perm_delete(self):
        return self._perm_delete

    @property
    def perm_ac(self):
        return self._perm_ac
