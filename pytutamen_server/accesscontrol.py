# -*- coding: utf-8 -*-

# Andy Sayler
# Copyright 2015


### Imports ###

import datetime
import uuid
import logging
import importlib

from . import crypto
from . import utility
from . import constants
from . import datatypes

import authmods


### Constants ###

_PERM_SEPERATOR = "_"

_KEY_ACSRV = "accesscontrol"

_LABEL_AUTHORIZATIONS = "authorizations"
_LABEL_VERIFIERS = "verifiers"
_LABEL_AUTHENTICATORS = "authenticators"
_LABEL_ACCOUNTS = "accounts"
_LABEL_PERMISSIONS = "permissions"

_PREFIX_AUTHORIZATION = "authorization"
_PREFIX_VERIFIER = "verifier"
_PREFIX_AUTHENTICATOR = "authenticator"
_PREFIX_ACCOUNT = "account"
_PREFIX_CLIENT = "client"
_PREFIX_PERMISSIONS = "permissions"

_POSTFIX_CA_CRT = "ca_crt"
_POSTFIX_CA_KEY = "ca_key"
_POSTFIX_SIGKEY_PUB = "sigkey_pub"
_POSTFIX_SIGKEY_PRIV = "sigkey_priv"
_POSTFIX_CLIENT_CRT = "crt"
_POSTFIX_ACCOUNTUID = "accountuid"
_POSTFIX_CLIENTUID = "clientuid"
_POSTFIX_EXPIRATION = "expiration"
_POSTFIX_OBJPERM = "objperm"
_POSTFIX_OBJTYPE = "objtype"
_POSTFIX_OBJUID = "objuid"
_POSTFIX_STATUS = "status"
_POSTFIX_MODULE_NAME = "module_name"
_POSTFIX_MODULE_KWARGS = "module_kwargs"
_POSTFIX_VERIFIERS = "verifiers"
_POSTFIX_ACCOUNTS = "accounts"
_POSTFIX_AUTHENTICATORS = "authenticators"
_POSTFIX_BYPASS_ACCOUNTS = "bypass_accounts"
_POSTFIX_BYPASS_AUTHENTICATORS = "bypass_authenticators"
_POSTFIX_CLIENTS = "clients"


### Logging ###

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.NullHandler())


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

class AuthorizationAlreadyProcessed(AuthorizationException):

    def __init__(self, authz):

        # Check Args
        utility.check_isinstance(authz, Authorization)

        # Message
        msg = "Authorization {} has already been processed".format(authz.key)

        # Call Parent
        super().__init__(msg)


### Objects ###

class AccessControlServer(datatypes.ServerObject):

    def __init__(self, pbackend, key=_KEY_ACSRV, create=False,
                 ca_crt_pem=None, ca_key_pem=None,
                 sigkey_pub_pem=None, sigkey_priv_pem=None,
                 cn=None, country=None, state=None, locality=None,
                 org=None, ou=None, email=None):

        # Call Parent
        super().__init__(pbackend, key=key, create=create)

        # Setup Child Indexes
        self._authorizations = datatypes.ChildIndex(self, Authorization, _LABEL_AUTHORIZATIONS)
        self._verifiers = datatypes.ChildIndex(self, Verifier, _LABEL_VERIFIERS)
        self._authenticators = datatypes.ChildIndex(self, Authenticator, _LABEL_AUTHENTICATORS)
        self._accounts = datatypes.ChildIndex(self, Account, _LABEL_ACCOUNTS)
        self._permissions = datatypes.ChildIndex(self, Permissions, _LABEL_PERMISSIONS)

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
                utility.check_isinstance(org, str)
                utility.check_isinstance(ou, str)
                utility.check_isinstance(email, str)
                ca_crt_pem, ca_key_pem = crypto.gen_ca_pair(cn, country, state, locality,
                                                            org, ou, email,
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
        self._permissions.destroy()
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
    def permissions(self):
        return self._permissions

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
                 accountuid=None, clientuid=None, expiration=None,
                 objperm=None, objtype=None, objuid=None, **kwargs):
        """Initialize Authorization"""

        # Check Input
        utility.check_isinstance(pindex.parent, AccessControlServer)
        if create:
            utility.check_isinstance(accountuid, uuid.UUID)
            accountuid = str(accountuid)
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
            accountuid = None
            clientuid = None
            expiration = None
            objperm = None
            objtype = None
            objuid = None

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Data
        self._accountuid = self._build_pobj(self.pcollections.String,
                                           _POSTFIX_ACCOUNTUID,
                                           create=accountuid)
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
                                        create=constants.AUTHZ_STATUS_NEW)

    def destroy(self):
        """Delete Authorization"""

        # Cleanup Status and Token
        self._status.rem()
        self._objuid.rem()
        self._objtype.rem()
        self._objperm.rem()
        self._expiration.rem()
        self._clientuid.rem()
        self._accountuid.rem()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Access Control Server"""
        return self.parent

    @property
    def accountuid(self):
        """Return Account UID"""
        return uuid.UUID(self._accountuid.get_val())

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

        msg = "Verifying authorization '{}'".format(self)
        logger.debug(msg)

        # Check Status
        if (self.status != constants.AUTHZ_STATUS_NEW):
            msg = "Authorization already processed"
            logger.debug(msg)
            raise AuthorizationAlreadyProcessed(self)

        # Load Permissions
        try:
            perms = self.server.permissions.get(objtype=self.objtype, objuid=self.objuid)
        except datatypes.ObjectDNE as err:
            msg = "No such object: {} {}".format(self.objtype, self.objuid)
            logger.warning(msg)
            status = constants.AUTHZ_STATUS_FAILED + "_nosuchobj"
            self._status.set_val(status)
            return False
        except TypeError as err:
            msg = "Object '{}' missing objuid".format(self.objtype)
            logger.warning(msg)
            status = constants.AUTHZ_STATUS_FAILED + "_missingobjuid"
            self._status.set_val(status)
            return False

        msg = "Using permissions '{}'".format(perms)
        logger.debug(msg)

        # Load Verifiers
        try:
            verifiers = perms.verifiers[self.objperm]
        except KeyError as err:
            msg = "No such permission '{}'".format(self.objperm)
            logger.warning(msg)
            status = constants.AUTHZ_STATUS_FAILED + "_nosuchperm"
            self._status.set_val(status)
            return False

        msg = "Using verifiers '{}'".format(verifiers)
        logger.debug(msg)

        # Search for valid verifiers
        passed_accounts = False
        passed_authenticators = False
        for verifier in verifiers.by_obj():

            # Check Account
            if verifier.bypass_accounts:
                msg = "Bypassing Account Verification"
                logger.debug(msg)
                passed_accounts = True
            elif verifier.accounts.ismember(self.accountuid):
                msg = "Account '{}' matches verifier '{}'".format(self.accountuid, verifier)
                logger.debug(msg)
                passed_accounts = True
            else:
                msg = "No matching accounts found"
                logger.debug(msg)
                passed_accounts = False

            # Check Authenticators
            passed_authenticators = False
            if verifier.bypass_authenticators:
                msg = "Bypassing Authenticator Verification"
                logger.debug(msg)
                passed_authenticators = True
            else:
                # Todo: verify authenticators
                passed_authenticators = True

        # Set Status and Return
        if passed_accounts and passed_authenticators:
            self._status.set_val(constants.AUTHZ_STATUS_APPROVED)
        else:
            self._status.set_val(constants.AUTHZ_STATUS_DENIED)
        msg = "passed_accounts = '{}', ".format(passed_accounts)
        msg += "passed_authenticators = '{}', ".format(passed_authenticators)
        msg += "status = '{}'".format(self.status)
        logger.debug(msg)
        return (passed_accounts and passed_authenticators)

    def export_token(self):
        """Get signed assertion token"""

        if self.status != constants.AUTHZ_STATUS_APPROVED:
            raise AuthorizationNotApproved(self)

        token = utility.encode_auth_token(self.server.sigkey_priv,
                                          self.accountuid,
                                          self.clientuid,
                                          self.expiration,
                                          self.objperm,
                                          self.objtype,
                                          self.objuid)

        # Assertion Check
        val = utility.decode_auth_token(self.server.sigkey_pub, token)
        assert(val[utility.AUTHZ_KEY_ACCOUNTUID] == self.accountuid)
        assert(val[utility.AUTHZ_KEY_CLIENTUID] == self.clientuid)
        assert(val[utility.AUTHZ_KEY_EXPIRATION] == self.expiration)
        assert(val[utility.AUTHZ_KEY_OBJPERM] == self.objperm)
        assert(val[utility.AUTHZ_KEY_OBJTYPE] == self.objtype)
        assert(val[utility.AUTHZ_KEY_OBJUID] == self.objuid)

        return token

class Verifier(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_VERIFIER,
                 accounts=None, authenticators=None,
                 bypass_accounts=None, bypass_authenticators=None, **kwargs):
        """Initialize Verifier"""

        # Check Input
        utility.check_isinstance(pindex.parent, AccessControlServer)
        if accounts is None:
            accounts = []
        if authenticators is None:
            authenticators = []
        if bypass_accounts is None:
            bypass_accounts = False
        if bypass_authenticators is None:
            bypass_authenticators = False
        utility.check_isinstance(accounts, list)
        utility.check_isinstance(authenticators, list)
        utility.check_isinstance(bypass_accounts, bool)
        utility.check_isinstance(bypass_authenticators, bool)

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Objects
        self._bypass_accounts = self._build_pobj(self.pcollections.MutableString,
                                                 _POSTFIX_BYPASS_ACCOUNTS,
                                                 create=str(int(bypass_accounts)))
        self._bypass_authenticators = self._build_pobj(self.pcollections.MutableString,
                                                 _POSTFIX_BYPASS_AUTHENTICATORS,
                                                 create=str(int(bypass_authenticators)))

        # Setup Index
        def account_masters(key, **kwargs):
            return Account(self.pbackend, key=key, **kwargs).verifiers
        self._accounts = datatypes.MasterObjIndex(self, _POSTFIX_ACCOUNTS,
                                                  account_masters,
                                                  Account,
                                                  pindex=self.server.accounts)
        def authenticator_masters(key, **kwargs):
            return Authenticator(self.pbackend, key=key, **kwargs).verifiers
        self._authenticators = datatypes.MasterObjIndex(self, _POSTFIX_AUTHENTICATORS,
                                                        authenticator_masters,
                                                        Authenticator,
                                                        pindex=self.server.authenticators)

        # Add initial index values:
        if create:
            for account in accounts:
                self.accounts.add(account)
            for authenticator in authenticators:
                self.autenticators.add(authenticator)

    def destroy(self):
        """Delete Verifier"""

        # Cleanup Indexes
        self._authenticators.destroy()
        self._accounts.destroy()

        # Cleanup Objects
        self._bypass_authenticators.rem()
        self._bypass_accounts.rem()

        # Call Parent
        super().destroy()

    @property
    def server(self):
        """Return Access Control Server"""
        return self.parent

    @property
    def bypass_accounts(self):
        """Bypass Accounts Bool"""
        return bool(int(self._bypass_accounts.get_val()))

    @property
    def bypass_authenticators(self):
        """Bypass Authenticators Bool"""
        return bool(int(self._bypass_authenticators.get_val()))

    @property
    def accounts(self):
        """Return Accounts Object Index"""
        return self._accounts

    @property
    def authenticators(self):
        """Return Authenticators Object Index"""
        return self._authenticators

class Authenticator(datatypes.UUIDObject, datatypes.UserDataObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 prefix=_PREFIX_AUTHENTICATOR,
                 module_name=None, module_kwargs=None, **kwargs):
        """Initialize Authenticator"""

        # Check Input
        utility.check_isinstance(pindex.parent, AccessControlServer)
        module = None
        if create:
            utility.check_isinstance(module_name, str)
            module_kwargs = {} if (module_kwargs is None) else module_kwargs
            utility.check_isinstance(module_kwargs, dict)
        else:
            module_name = None
            module_kwargs = None

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create, prefix=prefix, **kwargs)

        # Setup Vars
        def verifier_slaves(key, **kwargs):
            return Verifier(self.pbackend, key=key, **kwargs).authenticators
        self._verifiers = datatypes.SlaveObjIndex(self, _POSTFIX_VERIFIERS,
                                                  verifier_slaves,
                                                  Verifier,
                                                  pindex=self.server.verifiers)
        self._module_name = self._build_pobj(self.pcollections.String,
                                             _POSTFIX_MODULE_NAME,
                                             create=module_name)
        self._module_kwargs = self._build_pobj(self.pcollections.Dictionary,
                                               _POSTFIX_MODULE_KWARGS,
                                               create=module_kwargs)

        # Setup Module
        import_name = self._to_import_name(self.module_name)
        try:
            module = importlib.import_module(import_name, package='authmods')
            instance = module.Authmod(self, **self.module_kwargs)
        except Exception as err:
            self.destroy()
            raise
        else:
            self._module = module
            self._instance = instance

    def _to_import_name(self, module_name):
        module_name = module_name.lstrip('.')
        return ".{}".format(module_name)

    def destroy(self):
        """Delete Authenticator"""

        # Cleanup Vars
        self._module_kwargs.rem()
        self._module_name.rem()
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
    def module_name(self):
        """Return Module Name"""
        return self._module_name.get_val()

    @property
    def module_kwargs(self):
        """Return Module Name"""
        return self._module_kwargs.get_val()

    def run(self, authenticator):
        return self._instance.run(authenticator)


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
                                        cn=self.key, ou=self.account.key,
                                        serial=self.uid.int, org=str(self.account.uid.int))
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

class Permissions(datatypes.PermissionsObject, datatypes.ChildObject):

    def __init__(self, pbackend, pindex=None, create=False,
                 v_create=None, v_read=None,
                 v_modify=None, v_delete=None,
                 v_perms=None, v_default=None,
                 **kwargs):
        """Initialize Permissions"""

        # Check Input
        utility.check_isinstance(pindex.parent, AccessControlServer)
        if create:

            # Normalize
            v_create = self._normalize_verifiers(v_create)
            v_read = self._normalize_verifiers(v_read)
            v_modify = self._normalize_verifiers(v_modify)
            v_delete = self._normalize_verifiers(v_delete)
            v_perms = self._normalize_verifiers(v_perms)
            v_default = self._normalize_verifiers(v_default)

            # Use Defaults
            if v_default is not None:
                if v_create is None:
                    v_create = v_default
                if v_read is None:
                    v_read = v_default
                if v_modify is None:
                    v_modify = v_default
                if v_delete is None:
                    v_delete = v_default
                if v_perms is None:
                    v_perms = v_default

        else:

            # Zero
            v_create = None
            v_read = None
            v_modify = None
            v_delete = None
            v_perms = None
            v_default = None

        # Call Parent
        super().__init__(pbackend, pindex=pindex, create=create,
                         prefix=_PREFIX_PERMISSIONS, **kwargs)

        if self.objtype not in constants.SRV_TYPES:
            if not self.objuid:
                raise TypeError("Non-server types require objuid")

        # Setup Vars
        create_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_CREATE
        self._v_create = datatypes.PlainObjIndex(self, create_label, Verifier,
                                                 pindex=self.server.verifiers, init=v_create)
        read_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_READ
        self._v_read = datatypes.PlainObjIndex(self, read_label, Verifier,
                                               pindex=self.server.verifiers, init=v_read)
        modify_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_MODIFY
        self._v_modify = datatypes.PlainObjIndex(self, modify_label, Verifier,
                                                 pindex=self.server.verifiers, init=v_modify)
        delete_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_DELETE
        self._v_delete = datatypes.PlainObjIndex(self, delete_label, Verifier,
                                                 pindex=self.server.verifiers, init=v_delete)
        perms_label = _POSTFIX_VERIFIERS + _PERM_SEPERATOR + constants.PERM_PERMS
        self._v_perms = datatypes.PlainObjIndex(self, perms_label, Verifier,
                                                pindex=self.server.verifiers, init=v_perms)

    def destroy(self):
        """Delete Account"""

        # Cleanup Indexes
        self._v_perms.destroy()
        self._v_delete.destroy()
        self._v_modify.destroy()
        self._v_read.destroy()
        self._v_create.destroy()

        # Call Parent
        super().destroy()

    def _normalize_verifiers(self, verifiers):

        if verifiers is None:
            return None

        out = []
        for verifier in verifiers:
            if isinstance(verifier, Verifier):
                out.append(verifier.key)
            elif isinstance(verifier, uuid.UUID):
                out.append(str(verifier))
            elif isinstance(verifier, str):
                out.append(verifier)
            else:
                raise TypeError("Unsupported verifier type: '{}'".format(type(verifier)))

        return out

    @property
    def server(self):
        """Return Access Control Server"""
        return self.parent

    @property
    def v_create(self):
        return self._v_create

    @property
    def v_read(self):
        return self._v_read

    @property
    def v_modify(self):
        return self._v_modify

    @property
    def v_delete(self):
        return self._v_delete

    @property
    def v_perms(self):
        return self._v_perms

    @property
    def verifiers(self):
        return { constants.PERM_CREATE: self.v_create,
                 constants.PERM_READ: self.v_read,
                 constants.PERM_MODIFY: self.v_modify,
                 constants.PERM_DELETE: self.v_delete,
                 constants.PERM_PERMS: self.v_perms }
