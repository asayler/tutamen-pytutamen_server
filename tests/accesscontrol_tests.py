#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Access Control Tests


### Imports ###

## stdlib ##
import functools
import datetime
import uuid
import unittest

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

## Tests ##
import tests_common
import helpers

## tutamen_server ##
from pytutamen_server import crypto
from pytutamen_server import utility
from pytutamen_server import constants
from pytutamen_server import datatypes
from pytutamen_server import accesscontrol


### Object Classes ###

class AccessControlTestCase(tests_common.BaseTestCase):

    @classmethod
    def setUpClass(cls):

        # Call Parent
        super().setUpClass()

        cls.ca_key_pem = crypto.gen_key()
        cls.sigkey_priv_pem = crypto.gen_key()

    @classmethod
    def tearDownClass(cls):

        # Call Parent
        super().tearDownClass()

    def _create_accesscontrolserver(self, pbackend, **kwargs_user):

        cn = "Test Tutamen AC CA"
        country = "US"
        state = "Colorado"
        locality = "Boulder"
        org = "Test Tutamen AC Server"
        ou = "Test CA"
        email = "test@test.null"
        kwargs = {'cn': cn, 'country': country, 'state': state, 'locality': locality,
                  'org': org, 'ou': ou, 'email': email,
                  'ca_key_pem': self.ca_key_pem, 'sigkey_priv_pem': self.sigkey_priv_pem}
        kwargs.update(kwargs_user)

        acs = accesscontrol.AccessControlServer(pbackend, create=True, **kwargs)
        return acs

    def _create_authorization(self, acs, **kwargs_user):

        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = datetime.datetime.now()
        objperm = 'TESTPERM'
        objtype = 'TESTOBJ'
        objuid = uuid.uuid4()
        kwargs = {'accountuid': accountuid, 'clientuid': clientuid, 'expiration': expiration,
                  'objperm': objperm, 'objtype': objtype, 'objuid': objuid}
        kwargs.update(kwargs_user)

        authorization = acs.authorizations.create(**kwargs)
        return authorization

    def _create_verifier(self, acs, **kwargs_user):

        kwargs = {}
        kwargs.update(kwargs_user)

        verifier = acs.verifiers.create(**kwargs)
        return verifier

    def _create_authenticator(self, acs, **kwargs_user):

        module = 'TESTMOD'
        kwargs = {'module': module}
        kwargs.update(kwargs_user)

        authenticator = acs.authenticators.create(**kwargs)
        return authenticator

    def _create_account(self, acs, **kwargs_user):

        kwargs = {}
        kwargs.update(kwargs_user)

        account = acs.accounts.create(**kwargs)
        return account

    def _create_account_from_authz(self, authz, **kwargs_user):

        kwargs = {}
        kwargs['uid'] = authz.accountuid
        kwargs.update(kwargs_user)

        account = authz.server.accounts.create(**kwargs)
        return account

    def _create_client(self, acct, **kwargs_user):

        csr_pem = \
'''-----BEGIN CERTIFICATE REQUEST-----
MIICzDCCAbQCAQAwgYYxCzAJBgNVBAYTAlVTMREwDwYDVQQIDAhDb2xvcmFkbzEQ
MA4GA1UEBwwHQm91bGRlcjERMA8GA1UECgwIVGVzdCBPcmcxEjAQBgNVBAsMCVRl
c3QgVW5pdDENMAsGA1UEAwwEVGVzdDEcMBoGCSqGSIb3DQEJARYNdGVzdEB0ZXN0
LmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANPPAaEUAl4LNfRu
fQ703c7omWUS5dk17OxvJTeNGOIiWpqUdKfTDbAqGaxE93RXnoENUJ/3FtsIf2b1
CiZmrWuCDg510KCfvHKgH+okzvuYRTWATmG0LeCHfdWJWAoPkgTjVI2BBeIZw+ry
dpxS2Qtv/FojbwK8IRYUET31GyndkfV84gviw0z7RgtyCITyzhEWtP3I9ykU5Jtt
0HYe+Lk7fg37WyapS0mIGJSwwVMC7zwt++GSP/NiwtGrDodfhIRQX4bzYi7Mv2Zs
jo2xQ4+BjAhleymQJ82R+htV9GszBAo8HgD2e6EhpO4c9/ujDzWtmabBoLs1g9MB
0BXNKnMCAwEAAaAAMA0GCSqGSIb3DQEBCwUAA4IBAQCz2MjucM8T3ojWagftOBn4
+Mgsyl2HCmjU4k66ySwRQEf2ilUtA65x2xcsbH4VqdOYDWqm6umsrBe52KAz/Lul
FE5lngVlgNes9Od75vpg3FZjLktSJCafhddx7/0iM2HYiu8kt5Bg7CHh7J7O+g39
2WRLYZnLiUtFYFL7sQ6AKNg37P2Uzm9wkXoJYH4NU1HmEk6onMQB3D+95EbE3Oyh
WW0nx4pTG4AUOJdjOA8kQejN9afcHJqRTuUEu5qlC4no9OsO3YeyyO5gFNXhpoSu
8SjXBMpPV9DD/89eGjWtiJLruqdXI/AjEqQYeLuykSr5WMv8kNTC852VIQrp5+iy
-----END CERTIFICATE REQUEST-----'''
        kwargs = {}
        kwargs = {'csr_pem': csr_pem}
        kwargs.update(kwargs_user)

        client = acct.clients.create(**kwargs)
        return client

    def _create_permissions(self, acs, **kwargs_user):

        kwargs = {}
        kwargs['objtype'] = "testobj"
        kwargs['objuid'] = uuid.uuid4()
        kwargs.update(kwargs_user)

        perms = acs.permissions.create(**kwargs)
        return perms

    def _create_permissions_from_authz(self, authz, **kwargs_user):

        kwargs = {}
        kwargs['objtype'] = authz.objtype
        kwargs['objuid'] = authz.objuid
        kwargs.update(kwargs_user)

        perms = authz.server.permissions.create(**kwargs)
        return perms

class AccessControlServerTestCase(AccessControlTestCase, helpers.ObjectsHelpers):

    def test_init_and_destroy(self):

        # Create Server (New Keys)
        kwargs = {'ca_key_pem': None, 'sigkey_priv_pem': None}
        acs = self._create_accesscontrolserver(self.pbackend, **kwargs)
        self.assertIsInstance(acs, accesscontrol.AccessControlServer)

        # Create Server (Cached Keys)
        kwargs = {'ca_key_pem': self.ca_key_pem, 'sigkey_priv_pem': self.sigkey_priv_pem}
        acs = self._create_accesscontrolserver(self.pbackend, **kwargs)
        self.assertIsInstance(acs, accesscontrol.AccessControlServer)

        # Cleanup
        acs.destroy()

    def test_authorizations(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test Authorizations
        self.assertIsInstance(acs.authorizations, datatypes.ChildIndex)
        self.assertEqual(acs.authorizations.type_child, accesscontrol.Authorization)
        self.assertEqual(acs.authorizations.parent, acs)

        # Cleanup
        acs.destroy()

    def test_verifiers(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test Verifiers
        self.assertIsInstance(acs.verifiers, datatypes.ChildIndex)
        self.assertEqual(acs.verifiers.type_child, accesscontrol.Verifier)
        self.assertEqual(acs.verifiers.parent, acs)

        # Cleanup
        acs.destroy()

    def test_authenticators(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test Authenticators
        self.assertIsInstance(acs.authenticators, datatypes.ChildIndex)
        self.assertEqual(acs.authenticators.type_child, accesscontrol.Authenticator)
        self.assertEqual(acs.authenticators.parent, acs)

        # Cleanup
        acs.destroy()

    def test_accounts(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test Accounts
        self.assertIsInstance(acs.accounts, datatypes.ChildIndex)
        self.assertEqual(acs.accounts.type_child, accesscontrol.Account)
        self.assertEqual(acs.accounts.parent, acs)

        # Cleanup
        acs.destroy()

    def test_permissions(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test Accounts
        self.assertIsInstance(acs.permissions, datatypes.ChildIndex)
        self.assertEqual(acs.permissions.type_child, accesscontrol.Permissions)
        self.assertEqual(acs.permissions.parent, acs)

        # Cleanup
        acs.destroy()

    def test_ca_crt(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test Accounts
        self.assertIsInstance(acs.ca_crt, str)
        self.assertGreater(len(acs.ca_crt), 0)
        ca_crt = x509.load_pem_x509_certificate(acs.ca_crt.encode(), default_backend())
        self.assertGreater(ca_crt.serial, 0)

        # Cleanup
        acs.destroy()

    def test_ca_key(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test Accounts
        self.assertIsInstance(acs.ca_key, str)
        self.assertGreater(len(acs.ca_key), 0)
        ca_key = serialization.load_pem_private_key(acs.ca_key.encode(), None, default_backend())
        self.assertGreater(ca_key.key_size, 0)

        # Cleanup
        acs.destroy()

    def test_sigkey_pub(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test sig_pub
        self.assertIsInstance(acs.sigkey_pub, str)
        self.assertGreater(len(acs.sigkey_pub), 0)
        sigkey_pub = serialization.load_pem_public_key(acs.sigkey_pub.encode(), default_backend())
        self.assertGreater(sigkey_pub.key_size, 0)

        # Cleanup
        acs.destroy()

    def test_sigkey_priv(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)

        # Test sig_pub
        self.assertIsInstance(acs.sigkey_priv, str)
        self.assertGreater(len(acs.sigkey_priv), 0)
        sigkey_priv = serialization.load_pem_private_key(acs.sigkey_priv.encode(),
                                                          None, default_backend())
        self.assertGreater(sigkey_priv.key_size, 0)

        # Cleanup
        acs.destroy()

class AuthorizationTestCase(AccessControlTestCase, helpers.ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver(self.pbackend)

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_authorization, self.acs)
        self.helper_test_obj_create(accesscontrol.Authorization,
                                    self.acs.authorizations,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_authorization, self.acs)
        get_obj = self.acs.authorizations.get
        self.helper_test_obj_existing(accesscontrol.Authorization,
                                      self.acs.authorizations,
                                      create_obj, get_obj)

    def test_server(self):

        # Create Authorization
        auth = self._create_authorization(self.acs)

        # Test Server
        self.assertEqual(auth.server, self.acs)

        # Cleanup
        auth.destroy()

    def test_accountuid(self):

        # Create Authorization
        accountuid = uuid.uuid4()
        auth = self._create_authorization(self.acs, accountuid=accountuid)

        # Test Account UID
        self.assertEqual(auth.accountuid, accountuid)

        # Cleanup
        auth.destroy()

    def test_clientuid(self):

        # Create Authorization
        clientuid = uuid.uuid4()
        auth = self._create_authorization(self.acs, clientuid=clientuid)

        # Test Client UID
        self.assertEqual(auth.clientuid, clientuid)

        # Cleanup
        auth.destroy()

    def test_expiration(self):

        # Create Authorization
        expiration = datetime.datetime.utcnow()
        auth = self._create_authorization(self.acs, expiration=expiration)

        # Test Expiration
        self.assertAlmostEqual(auth.expiration.timestamp(), expiration.timestamp(), delta=1)

        # Cleanup
        auth.destroy()

    def test_expiration_timestamp(self):

        # Create Authorization
        expiration = datetime.datetime.now()
        auth = self._create_authorization(self.acs, expiration=expiration)

        # Test Expiration Timestamp
        self.assertAlmostEqual(auth.expiration_timestamp, expiration.timestamp(), delta=1)

        # Cleanup
        auth.destroy()

    def test_objperm(self):

        # Create Authorization
        objperm = 'TESTPERM2'
        auth = self._create_authorization(self.acs, objperm=objperm)

        # Test Expriation
        self.assertEqual(auth.objperm, objperm)

        # Cleanup
        auth.destroy()

    def test_objtype(self):

        # Create Authorization
        objtype = 'TESTOBJ'
        auth = self._create_authorization(self.acs, objtype=objtype)

        # Test Expriation
        self.assertEqual(auth.objtype, objtype)

        # Cleanup
        auth.destroy()

    def test_objuid(self):

        # Create Authorization
        objuid = uuid.uuid4()
        auth = self._create_authorization(self.acs, objuid=objuid)

        # Test Expriation
        self.assertEqual(auth.objuid, objuid)

        # Cleanup
        auth.destroy()

    def test_status(self):

        # Create Authorization
        auth = self._create_authorization(self.acs)

        # Test Status
        self.assertEqual(auth.status, constants.AUTHZ_STATUS_NEW)

        # Cleanup
        auth.destroy()

    def test_verify_pass(self):

        # Create Authorization
        auth = self._create_authorization(self.acs, objperm="read")
        acct = self._create_account_from_authz(auth)
        verifier = self._create_verifier(self.acs, accounts=[acct])
        perms = self._create_permissions_from_authz(auth, v_default=[verifier])

        # Test Verify (Valid)
        self.assertEqual(auth.status, constants.AUTHZ_STATUS_NEW)
        self.assertTrue(auth.verify())
        self.assertEqual(auth.status, constants.AUTHZ_STATUS_APPROVED)

        # Test Verify (Already processed)
        self.assertRaises(accesscontrol.AuthorizationAlreadyProcessed, auth.verify)

        # Cleanup
        perms.destroy()
        verifier.destroy()
        acct.destroy()
        auth.destroy()

    def test_verify_fail_noperm(self):

        # Create Authorization
        auth = self._create_authorization(self.acs, objperm="read")
        acct = self._create_account_from_authz(auth)

        # Test Verify (Invalid)
        self.assertEqual(auth.status, constants.AUTHZ_STATUS_NEW)
        self.assertFalse(auth.verify())
        self.assertEqual(auth.status.split('_')[0], constants.AUTHZ_STATUS_FAILED)

        # Test Verify (Already processed)
        self.assertRaises(accesscontrol.AuthorizationAlreadyProcessed, auth.verify)

        # Cleanup
        acct.destroy()
        auth.destroy()

    def test_verify_fail_badperm(self):

        # Create Authorization
        auth = self._create_authorization(self.acs, objperm="fake")
        acct = self._create_account_from_authz(auth)
        perms = self._create_permissions_from_authz(auth)

        # Test Verify (Invalid)
        self.assertEqual(auth.status, constants.AUTHZ_STATUS_NEW)
        self.assertFalse(auth.verify())
        self.assertEqual(auth.status.split('_')[0], constants.AUTHZ_STATUS_FAILED)

        # Test Verify (Already processed)
        self.assertRaises(accesscontrol.AuthorizationAlreadyProcessed, auth.verify)

        # Cleanup
        perms.destroy()
        acct.destroy()
        auth.destroy()

    def test_verify_deny(self):

        # Create Authorization
        auth = self._create_authorization(self.acs, objperm="read")
        acct = self._create_account_from_authz(auth)
        perms = self._create_permissions_from_authz(auth)

        # Test Verify (Invalid)
        self.assertEqual(auth.status, constants.AUTHZ_STATUS_NEW)
        self.assertFalse(auth.verify())
        self.assertEqual(auth.status, constants.AUTHZ_STATUS_DENIED)

        # Test Verify (Already processed)
        self.assertRaises(accesscontrol.AuthorizationAlreadyProcessed, auth.verify)

        # Cleanup
        perms.destroy()
        acct.destroy()
        auth.destroy()

    def test_export_token(self):

        # Create Authorization
        auth = self._create_authorization(self.acs, objperm="read")
        acct = self._create_account_from_authz(auth)
        verifier = self._create_verifier(self.acs, accounts=[acct])
        perms = self._create_permissions_from_authz(auth, v_default=[verifier])

        # Test Unapproved
        self.assertRaises(accesscontrol.AuthorizationNotApproved, auth.export_token)

        # Approve
        self.assertTrue(auth.verify())

        # Test Approved
        token = auth.export_token()
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)

        # Test Decode
        val = utility.decode_auth_token(self.acs.sigkey_pub, token)
        self.assertIsInstance(val, dict)
        self.assertGreater(len(val), 0)

        # Cleanup
        perms.destroy()
        verifier.destroy()
        acct.destroy()
        auth.destroy()

class VerifierTestCase(AccessControlTestCase, helpers.ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver(self.pbackend)

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_verifier, self.acs)
        self.helper_test_obj_create(accesscontrol.Verifier,
                                    self.acs.verifiers,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_verifier, self.acs)
        get_obj = self.acs.verifiers.get
        self.helper_test_obj_existing(accesscontrol.Verifier,
                                      self.acs.verifiers,
                                      create_obj, get_obj)

    def test_server(self):

        # Create Verifier
        verf = self._create_verifier(self.acs)

        # Test Server
        self.assertEqual(verf.server, self.acs)

        # Cleanup
        verf.destroy()

    def test_authenticators(self):

        # Create Verifier
        verf = self._create_verifier(self.acs)

        # Test Authenticators
        self.assertIsInstance(verf.authenticators, datatypes.MasterObjIndex)
        self.assertEqual(verf.authenticators.obj, verf)

        # Test Server
        self.assertEqual(verf.server, self.acs)

        # Cleanup
        verf.destroy()

    def test_authenticators_ops(self):

        create_master = functools.partial(self._create_verifier, self.acs)
        create_slave = functools.partial(self._create_authenticator, self.acs)
        get_master_index = lambda master: master.authenticators
        self.helper_test_master_obj_index(create_master, create_slave,
                                          get_master_index)

    def test_accounts(self):

        # Create Verifier
        verf = self._create_verifier(self.acs)

        # Test Accounts
        self.assertIsInstance(verf.accounts, datatypes.MasterObjIndex)
        self.assertEqual(verf.accounts.obj, verf)

        # Test Server
        self.assertEqual(verf.server, self.acs)

        # Cleanup
        verf.destroy()

    def test_accounts_ops(self):

        create_master = functools.partial(self._create_verifier, self.acs)
        create_slave = functools.partial(self._create_account, self.acs)
        get_master_index = lambda master: master.accounts
        self.helper_test_master_obj_index(create_master, create_slave,
                                          get_master_index)

class AuthenticatorTestCase(AccessControlTestCase, helpers.ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver(self.pbackend)

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_authenticator, self.acs)
        self.helper_test_obj_create(accesscontrol.Authenticator,
                                    self.acs.authenticators,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_authenticator, self.acs)
        get_obj = self.acs.authenticators.get
        self.helper_test_obj_existing(accesscontrol.Authenticator,
                                      self.acs.authenticators,
                                      create_obj, get_obj)

    def test_server(self):

        # Create Authenticator
        auth = self._create_authenticator(self.acs)

        # Test Server
        self.assertEqual(auth.server, self.acs)

        # Cleanup
        auth.destroy()

    def test_verifiers(self):

        # Create Authenticator
        auth = self._create_authenticator(self.acs)

        # Test Server
        self.assertIsInstance(auth.verifiers, datatypes.SlaveObjIndex)
        self.assertEqual(auth.verifiers.obj, auth)

        # Cleanup
        auth.destroy()

    def test_verifiers_ops(self):

        create_master = functools.partial(self._create_verifier, self.acs)
        create_slave = functools.partial(self._create_authenticator, self.acs)
        get_master_index = lambda master: master.authenticators
        get_slave_index = lambda slave: slave.verifiers
        self.helper_test_slave_obj_index(create_master, create_slave,
                                         get_master_index, get_slave_index)

    def test_module(self):

        # Create Authenticator
        module = 'TESTMODULE'
        auth = self._create_authenticator(self.acs, module=module)

        # Test Client UID
        self.assertEqual(auth.module, module)

        # Cleanup
        auth.destroy()

class AccountTestCase(AccessControlTestCase, helpers.ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver(self.pbackend)

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_account, self.acs)
        self.helper_test_obj_create(accesscontrol.Account,
                                    self.acs.accounts,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_account, self.acs)
        get_obj = self.acs.accounts.get
        self.helper_test_obj_existing(accesscontrol.Account,
                                      self.acs.accounts,
                                      create_obj, get_obj)

    def test_server(self):

        # Create Account
        acct = self._create_account(self.acs)

        # Test Server
        self.assertEqual(acct.server, self.acs)

        # Cleanup
        acct.destroy()

    def test_clients(self):

        # Create Server
        acct = self._create_account(self.acs)

        # Test Clients
        self.assertIsInstance(acct.clients, datatypes.ChildIndex)
        self.assertEqual(acct.clients.type_child, accesscontrol.Client)
        self.assertEqual(acct.clients.parent, acct)

        # Cleanup
        acct.destroy()

    def test_verifiers(self):

        # Create Authenticator
        acct = self._create_account(self.acs)

        # Test Server
        self.assertIsInstance(acct.verifiers, datatypes.SlaveObjIndex)
        self.assertEqual(acct.verifiers.obj, acct)

        # Cleanup
        acct.destroy()

    def test_verifiers_ops(self):

        create_master = functools.partial(self._create_verifier, self.acs)
        create_slave = functools.partial(self._create_account, self.acs)
        get_master_index = lambda master: master.accounts
        get_slave_index = lambda slave: slave.verifiers
        self.helper_test_slave_obj_index(create_master, create_slave,
                                         get_master_index, get_slave_index)

class ClientTestCase(AccessControlTestCase, helpers.ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver(self.pbackend)
        self.acct = self._create_account(self.acs)

    def tearDown(self):

        # Teardown Properties
        self.acct.destroy()
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_client, self.acct)
        self.helper_test_obj_create(accesscontrol.Client,
                                    self.acct.clients,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_client, self.acct)
        get_obj = self.acct.clients.get
        self.helper_test_obj_existing(accesscontrol.Client,
                                      self.acct.clients,
                                      create_obj, get_obj)

    def test_server(self):

        # Create Client
        client = self._create_client(self.acct)

        # Test Server
        self.assertEqual(client.server, self.acs)

        # Cleanup
        client.destroy()

    def test_account(self):

        # Create Client
        client = self._create_client(self.acct)

        # Test Account
        self.assertEqual(client.account, self.acct)

        # Cleanup
        client.destroy()

    def test_crt(self):

        # Create Client
        client = self._create_client(self.acct)

        # Test Accounts
        self.assertIsInstance(client.crt, str)
        self.assertGreater(len(client.crt), 0)
        crt = x509.load_pem_x509_certificate(client.crt.encode(), default_backend())
        self.assertEqual(int(crt.serial), int(client.uid))
        cn = crt.subject.get_attributes_for_oid(x509.NameOID.COMMON_NAME)[0].value
        self.assertEqual(cn, client.key)
        ou = crt.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATIONAL_UNIT_NAME)[0].value
        self.assertEqual(ou, client.account.key)
        org = crt.subject.get_attributes_for_oid(x509.NameOID.ORGANIZATION_NAME)[0].value
        self.assertEqual(int(org), int(client.account.uid))

        # Cleanup
        client.destroy()

class Permissions(AccessControlTestCase, helpers.ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver(self.pbackend)

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_permissions, self.acs)
        self.helper_test_obj_create(accesscontrol.Permissions,
                                    self.acs.permissions,
                                    create_obj, uuidobj=False, permobj=True)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_permissions, self.acs)
        get_obj = self.acs.permissions.get
        self.helper_test_obj_existing(accesscontrol.Permissions,
                                      self.acs.permissions,
                                      create_obj, get_obj, uuidobj=False, permobj=True)

    def test_server(self):

        # Create Perms
        perms = self._create_permissions(self.acs)

        # Test Server
        self.assertEqual(perms.server, self.acs)

        # Cleanup
        perms.destroy()

    def test_v_create(self):

        # Create Perms
        perms = self._create_permissions(self.acs)

        # Test v_create
        self.assertIsInstance(perms.v_create, datatypes.PlainObjIndex)
        self.assertEqual(perms.v_create.type_member, accesscontrol.Verifier)
        self.assertEqual(perms.v_create.obj, perms)

        # Cleanup
        perms.destroy()

    def test_v_read(self):

        # Create Perms
        perms = self._create_permissions(self.acs)

        # Test v_read
        self.assertIsInstance(perms.v_read, datatypes.PlainObjIndex)
        self.assertEqual(perms.v_read.type_member, accesscontrol.Verifier)
        self.assertEqual(perms.v_read.obj, perms)

        # Cleanup
        perms.destroy()

    def test_v_modify(self):

        # Create Perms
        perms = self._create_permissions(self.acs)

        # Test v_modify
        self.assertIsInstance(perms.v_modify, datatypes.PlainObjIndex)
        self.assertEqual(perms.v_modify.type_member, accesscontrol.Verifier)
        self.assertEqual(perms.v_modify.obj, perms)

        # Cleanup
        perms.destroy()

    def test_v_delete(self):

        # Create Perms
        perms = self._create_permissions(self.acs)

        # Test v_delete
        self.assertIsInstance(perms.v_delete, datatypes.PlainObjIndex)
        self.assertEqual(perms.v_delete.type_member, accesscontrol.Verifier)
        self.assertEqual(perms.v_delete.obj, perms)

        # Cleanup
        perms.destroy()

    def test_v_perms(self):

        # Create Perms
        perms = self._create_permissions(self.acs)

        # Test v_perms
        self.assertIsInstance(perms.v_perms, datatypes.PlainObjIndex)
        self.assertEqual(perms.v_perms.type_member, accesscontrol.Verifier)
        self.assertEqual(perms.v_perms.obj, perms)

        # Cleanup
        perms.destroy()

    def test_verifiers(self):

        # Create Perms
        perms = self._create_permissions(self.acs)

        # Test verifiers
        self.assertIsInstance(perms.verifiers, dict)
        self.assertIn(constants.PERM_CREATE, perms.verifiers)
        self.assertEqual(perms.verifiers[constants.PERM_CREATE], perms.v_create)
        self.assertIn(constants.PERM_READ, perms.verifiers)
        self.assertEqual(perms.verifiers[constants.PERM_READ], perms.v_read)
        self.assertIn(constants.PERM_MODIFY, perms.verifiers)
        self.assertEqual(perms.verifiers[constants.PERM_MODIFY], perms.v_modify)
        self.assertIn(constants.PERM_DELETE, perms.verifiers)
        self.assertEqual(perms.verifiers[constants.PERM_DELETE], perms.v_delete)
        self.assertIn(constants.PERM_PERMS, perms.verifiers)
        self.assertEqual(perms.verifiers[constants.PERM_PERMS], perms.v_perms)

        # Cleanup
        perms.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
