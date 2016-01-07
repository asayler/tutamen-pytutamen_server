#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Access Control Tests


### Imports ###

## stdlib ##
import functools
import time
import uuid
import unittest

# Tests Common
import tests_common

## tutamen_server ##
from pytutamen_server import datatypes
from pytutamen_server import accesscontrol


### Object Classes ###

class AccessControlTestCase(tests_common.BaseTestCase):

    def _create_accesscontrolserver(self, pbackend, **kwargs_user):

        kwargs = {}
        kwargs.update(kwargs_user)

        acs = accesscontrol.AccessControlServer(pbackend, **kwargs)
        return acs

    def _create_authorization(self, acs, **kwargs_user):

        clientuid = uuid.uuid4()
        expiration = time.time()
        objperm = 'TESTPERM'
        objtype = 'TESTOBJ'
        objuid = uuid.uuid4()
        kwargs = {'clientuid': clientuid, 'expiration': expiration,
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

    def _create_client(self, acct, **kwargs_user):

        kwargs = {}
        kwargs.update(kwargs_user)

        client = acct.clients.create(**kwargs)
        return client

class ObjectsHelpers(object):

    def helper_test_obj_create(self, obj_type, obj_index, create_obj):

        # Test Create (Random)
        obj = create_obj()
        self.assertIsInstance(obj, obj_type)
        self.assertTrue(obj.exists())
        self.assertTrue(obj_index.exists(obj))
        obj.destroy()

        # Test Create (Key)
        key = "eb424026-6f54-4ef8-a4d0-bb658a1fc6cf"
        obj = create_obj(key=key)
        self.assertIsInstance(obj, obj_type)
        self.assertTrue(obj.exists())
        self.assertTrue(obj_index.exists(obj))
        self.assertEqual(obj.key, key)
        obj.destroy()

        # Test Create (UID)
        uid = uuid.uuid4()
        obj = create_obj(uid=uid)
        self.assertIsInstance(obj, obj_type)
        self.assertTrue(obj.exists())
        self.assertTrue(obj_index.exists(obj))
        self.assertEqual(obj.uid, uid)
        obj.destroy()

    def helper_test_obj_existing(self, obj_type, obj_index, create_obj, get_obj):

        # Test DNE
        uid = uuid.uuid4()
        self.assertRaises(datatypes.ObjectDNE, get_obj, uid=uid)

        # Create Object
        obj = create_obj()
        key = obj.key
        uid = obj.uid

        # Test get (key)
        obj = get_obj(key=key)
        self.assertIsInstance(obj, obj_type)
        self.assertTrue(obj.exists())
        self.assertTrue(obj_index.exists(obj))
        self.assertEqual(obj.key, key)

        # Test get (uuid)
        obj = get_obj(uid=uid)
        self.assertIsInstance(obj, obj_type)
        self.assertTrue(obj.exists())
        self.assertTrue(obj_index.exists(obj))
        self.assertEqual(obj.uid, uid)

        # Cleanup
        obj.destroy()

    def helper_test_objects_list(self, srv, objtype, create_objs, list_objs):

        # List Objects (Empty)
        keys = list_objs()
        self.assertEqual(len(keys), 0)

        # Create Objects
        objs = []
        for i in range(10):
            objs.append(create_objs(srv))

        # List Objects (Full)
        keys = list_objs()
        self.assertEqual(len(keys), len(objs))
        for obj in objs:
            self.assertTrue(obj.key in keys)

        # Delete Objects
        for obj in objs:
            obj.destroy()

        # List Objects (Empty)
        keys = list_objs()
        self.assertEqual(len(keys), 0)

    def helper_test_objects_exists(self, srv, objtype, create_objs, exists_objs):

        # Test DNE (key)
        key = "fakekey"
        self.assertFalse(exists_objs(key=key))

        # Test DNE (uuid)
        uid = uuid.uuid4()
        self.assertFalse(exists_objs(uid=uid))

        # Create Object
        obj = create_objs(srv)
        key = obj.key
        uid = obj.uid

        # Test Exists (key)
        self.assertTrue(exists_objs(key=key))

        # Test Exists (uuid)
        self.assertTrue(exists_objs(uid=uid))

        # Delete Object
        obj.destroy()

        # Test DNE (key)
        self.assertFalse(exists_objs(key=key))

        # Test DNE (uuid)
        self.assertFalse(exists_objs(uid=uid))

class AccessControlServerTestCase(AccessControlTestCase, ObjectsHelpers):

    def test_init_and_destroy(self):

        # Create Server
        acs = self._create_accesscontrolserver(self.pbackend)
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

class AuthorizationTestCase(AccessControlTestCase, ObjectsHelpers):

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
        expiration = time.time()
        auth = self._create_authorization(self.acs, expiration=expiration)

        # Test Expriation
        self.assertEqual(auth.expiration, expiration)

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
        self.assertEqual(auth.status, accesscontrol._NEW_STATUS)

        # Cleanup
        auth.destroy()

class VerifierTestCase(AccessControlTestCase, ObjectsHelpers):

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

        # Create Authorization
        auth = self._create_authorization(self.acs)

        # Test Server
        self.assertEqual(auth.server, self.acs)

        # Cleanup
        auth.destroy()

    # def test_authenticators_by_key(self):

    #     # Create Verifier
    #     verf = self._create_verifier(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(verf.authenticators_by_key()), 0)

    #     # Add to authenticators
    #     actr_objs = set()
    #     actr_keys = set()
    #     for i in range(10):
    #         actr = self._create_authenticator(self.acs)
    #         verf.authenticators_add(actr)
    #         actr_objs.add(actr)
    #         actr_keys.add(actr.key)

    #     # Test Full
    #     self.assertEqual(verf.authenticators_by_key(), actr_keys)

    #     # Remove Authenticators
    #     for actr in actr_objs:
    #         actr.destroy()

    #     # Test Empty
    #     self.assertEqual(len(verf.authenticators_by_key()), 0)

    #     # Cleanup
    #     verf.destroy()

    # def test_authenticators_by_uid(self):

    #     # Create Verifier
    #     verf = self._create_verifier(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(verf.authenticators_by_uid()), 0)

    #     # Add to authenticators
    #     actr_objs = set()
    #     actr_uids = set()
    #     for i in range(10):
    #         actr = self._create_authenticator(self.acs)
    #         verf.authenticators_add(actr)
    #         actr_objs.add(actr)
    #         actr_uids.add(actr.uid)

    #     # Test Full
    #     self.assertEqual(verf.authenticators_by_uid(), actr_uids)

    #     # Remove Authenticators
    #     for actr in actr_objs:
    #         actr.destroy()

    #     # Test Empty
    #     self.assertEqual(len(verf.authenticators_by_uid()), 0)

    #     # Cleanup
    #     verf.destroy()

    # def test_authenticators_by_obj(self):

    #     # Create Verifier
    #     verf = self._create_verifier(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(verf.authenticators_by_obj()), 0)

    #     # Add to authenticators
    #     actr_objs = set()
    #     for i in range(10):
    #         actr = self._create_authenticator(self.acs)
    #         verf.authenticators_add(actr)
    #         actr_objs.add(actr)

    #     # Test Full
    #     self.assertEqual(verf.authenticators_by_obj(), actr_objs)

    #     # Remove Authenticators
    #     for actr in actr_objs:
    #         actr.destroy()

    #     # Test Empty
    #     self.assertEqual(len(verf.authenticators_by_obj()), 0)

    #     # Cleanup
    #     verf.destroy()

    # def test_authenticators_add_is_member(self):

    #     # Create Verifier and Authenticator
    #     verf = self._create_verifier(self.acs, direct=True)
    #     actr = self._create_authenticator(self.acs)

    #     # Test Add
    #     self.assertFalse(verf.authenticators_is_member(actr))
    #     self.assertFalse(verf in actr.verifiers_by_obj())
    #     verf.authenticators_add(actr)
    #     self.assertTrue(verf.authenticators_is_member(actr))
    #     self.assertTrue(verf in actr.verifiers_by_obj())

    #     # Cleanup
    #     actr.destroy()
    #     verf.destroy()

    # def test_authenticators_remove_is_member(self):

    #     # Create Verifier and Authenticator
    #     verf = self._create_verifier(self.acs, direct=True)
    #     actr = self._create_authenticator(self.acs)
    #     verf.authenticators_add(actr)

    #     # Test Remove
    #     self.assertTrue(verf.authenticators_is_member(actr))
    #     self.assertTrue(verf in actr.verifiers_by_obj())
    #     verf.authenticators_remove(actr)
    #     self.assertFalse(verf.authenticators_is_member(actr))
    #     self.assertFalse(verf in actr.verifiers_by_obj())

    #     # Cleanup
    #     actr.destroy()
    #     verf.destroy()

    # def test_accounts_by_key(self):

    #     # Create Verifier
    #     verf = self._create_verifier(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(verf.accounts_by_key()), 0)

    #     # Add to accounts
    #     acct_objs = set()
    #     acct_keys = set()
    #     for i in range(10):
    #         acct = self._create_account(self.acs)
    #         verf.accounts_add(acct)
    #         acct_objs.add(acct)
    #         acct_keys.add(acct.key)

    #     # Test Full
    #     self.assertEqual(verf.accounts_by_key(), acct_keys)

    #     # Remove Accounts
    #     for acct in acct_objs:
    #         acct.destroy()

    #     # Test Empty
    #     self.assertEqual(len(verf.accounts_by_key()), 0)

    #     # Cleanup
    #     verf.destroy()

    # def test_accounts_by_uid(self):

    #     # Create Verifier
    #     verf = self._create_verifier(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(verf.accounts_by_uid()), 0)

    #     # Add to accounts
    #     acct_objs = set()
    #     acct_uids = set()
    #     for i in range(10):
    #         acct = self._create_account(self.acs)
    #         verf.accounts_add(acct)
    #         acct_objs.add(acct)
    #         acct_uids.add(acct.uid)

    #     # Test Full
    #     self.assertEqual(verf.accounts_by_uid(), acct_uids)

    #     # Remove Accounts
    #     for acct in acct_objs:
    #         acct.destroy()

    #     # Test Empty
    #     self.assertEqual(len(verf.accounts_by_uid()), 0)

    #     # Cleanup
    #     verf.destroy()

    # def test_accounts_by_obj(self):

    #     # Create Verifier
    #     verf = self._create_verifier(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(verf.accounts_by_obj()), 0)

    #     # Add to accounts
    #     acct_objs = set()
    #     for i in range(10):
    #         acct = self._create_account(self.acs)
    #         verf.accounts_add(acct)
    #         acct_objs.add(acct)

    #     # Test Full
    #     self.assertEqual(verf.accounts_by_obj(), acct_objs)

    #     # Remove Accounts
    #     for acct in acct_objs:
    #         acct.destroy()

    #     # Test Empty
    #     self.assertEqual(len(verf.accounts_by_obj()), 0)

    #     # Cleanup
    #     verf.destroy()

    # def test_accounts_add_is_member(self):

    #     # Create Verifier and Account
    #     verf = self._create_verifier(self.acs, direct=True)
    #     acct = self._create_account(self.acs)

    #     # Test Add
    #     self.assertFalse(verf.accounts_is_member(acct))
    #     self.assertFalse(verf in acct.verifiers_by_obj())
    #     verf.accounts_add(acct)
    #     self.assertTrue(verf.accounts_is_member(acct))
    #     self.assertTrue(verf in acct.verifiers_by_obj())

    #     # Cleanup
    #     acct.destroy()
    #     verf.destroy()

    # def test_accounts_remove_is_member(self):

    #     # Create Verifier and Account
    #     verf = self._create_verifier(self.acs, direct=True)
    #     acct = self._create_account(self.acs)
    #     verf.accounts_add(acct)

    #     # Test Remove
    #     self.assertTrue(verf.accounts_is_member(acct))
    #     self.assertTrue(verf in acct.verifiers_by_obj())
    #     verf.accounts_remove(acct)
    #     self.assertFalse(verf.accounts_is_member(acct))
    #     self.assertFalse(verf in acct.verifiers_by_obj())

    #     # Cleanup
    #     acct.destroy()
    #     verf.destroy()

class AuthenticatorTestCase(AccessControlTestCase, ObjectsHelpers):

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

    def test_module(self):

        # Create Authenticator
        module = 'TESTMODULE'
        auth = self._create_authenticator(self.acs, module=module)

        # Test Client UID
        self.assertEqual(auth.module, module)

        # Cleanup
        auth.destroy()

    # def test_verifiers_by_key(self):

    #     # Create Authenticator
    #     actr = self._create_authenticator(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(actr.verifiers_by_key()), 0)

    #     # Add to verifiers
    #     verifier_objs = set()
    #     verifier_keys = set()
    #     for i in range(10):
    #         verifier = self._create_verifier(self.acs)
    #         verifier.authenticators_add(actr)
    #         verifier_objs.add(verifier)
    #         verifier_keys.add(verifier.key)

    #     # Test Full
    #     self.assertEqual(actr.verifiers_by_key(), verifier_keys)

    #     # Remove Verifiers
    #     for verifier in verifier_objs:
    #         verifier.destroy()

    #     # Test Empty
    #     self.assertEqual(len(actr.verifiers_by_key()), 0)

    #     # Cleanup
    #     actr.destroy()

    # def test_verifiers_by_uid(self):

    #     # Create Authenticator
    #     actr = self._create_authenticator(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(actr.verifiers_by_uid()), 0)

    #     # Add Verifiers
    #     verifier_objs = set()
    #     verifier_uids = set()
    #     for i in range(10):
    #         verifier = self._create_verifier(self.acs)
    #         verifier.authenticators_add(actr)
    #         verifier_objs.add(verifier)
    #         verifier_uids.add(verifier.uid)

    #     # Test Full
    #     self.assertEqual(actr.verifiers_by_uid(), verifier_uids)

    #     # Remove Verifiers
    #     for verifier in verifier_objs:
    #         verifier.destroy()

    #     # Test Empty
    #     self.assertEqual(len(actr.verifiers_by_uid()), 0)

    #     # Cleanup
    #     actr.destroy()

    # def test_verifiers_by_obj(self):

    #     # Create Authenticator
    #     actr = self._create_authenticator(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(actr.verifiers_by_obj()), 0)

    #     # Add Verifiers
    #     verifier_objs = set()
    #     for i in range(10):
    #         verifier = self._create_verifier(self.acs)
    #         verifier.authenticators_add(actr)
    #         verifier_objs.add(verifier)

    #     # Test Full
    #     self.assertEqual(actr.verifiers_by_obj(), verifier_objs)

    #     # Remove Verifiers
    #     for verifier in verifier_objs:
    #         verifier.destroy()

    #     # Test Empty
    #     self.assertEqual(len(actr.verifiers_by_obj()), 0)

    #     # Cleanup
    #     actr.destroy()

class AccountTestCase(AccessControlTestCase, ObjectsHelpers):

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

    # def test_verifiers_by_key(self):

    #     # Create Account
    #     acct = self._create_account(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(acct.verifiers_by_key()), 0)

    #     # Add to verifiers
    #     verifier_objs = set()
    #     verifier_keys = set()
    #     for i in range(10):
    #         verifier = self._create_verifier(self.acs)
    #         verifier.accounts_add(acct)
    #         verifier_objs.add(verifier)
    #         verifier_keys.add(verifier.key)

    #     # Test Full
    #     self.assertEqual(acct.verifiers_by_key(), verifier_keys)

    #     # Remove Verifiers
    #     for verifier in verifier_objs:
    #         verifier.destroy()

    #     # Test Empty
    #     self.assertEqual(len(acct.verifiers_by_key()), 0)

    #     # Cleanup
    #     acct.destroy()

    # def test_verifiers_by_uid(self):

    #     # Create Account
    #     acct = self._create_account(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(acct.verifiers_by_uid()), 0)

    #     # Add Verifiers
    #     verifier_objs = set()
    #     verifier_uids = set()
    #     for i in range(10):
    #         verifier = self._create_verifier(self.acs)
    #         verifier.accounts_add(acct)
    #         verifier_objs.add(verifier)
    #         verifier_uids.add(verifier.uid)

    #     # Test Full
    #     self.assertEqual(acct.verifiers_by_uid(), verifier_uids)

    #     # Remove Verifiers
    #     for verifier in verifier_objs:
    #         verifier.destroy()

    #     # Test Empty
    #     self.assertEqual(len(acct.verifiers_by_uid()), 0)

    #     # Cleanup
    #     acct.destroy()

    # def test_verifiers_by_obj(self):

    #     # Create Account
    #     acct = self._create_account(self.acs, direct=True)

    #     # Test Empty
    #     self.assertEqual(len(acct.verifiers_by_obj()), 0)

    #     # Add Verifiers
    #     verifier_objs = set()
    #     for i in range(10):
    #         verifier = self._create_verifier(self.acs)
    #         verifier.accounts_add(acct)
    #         verifier_objs.add(verifier)

    #     # Test Full
    #     self.assertEqual(acct.verifiers_by_obj(), verifier_objs)

    #     # Remove Verifiers
    #     for verifier in verifier_objs:
    #         verifier.destroy()

    #     # Test Empty
    #     self.assertEqual(len(acct.verifiers_by_obj()), 0)

    #     # Cleanup
    #     acct.destroy()

    # ## Client Tests ##

    # def test_clients_create(self):

    #     # Create Account
    #     acct = self._create_account(self.acs, direct=True)

    #     # Test Create
    #     create_obj = functools.partial(self._create_client, direct=False)
    #     self.helper_test_obj_create(acct, accesscontrol.Client,
    #                                 create_obj)

    #     # Cleanup
    #     acct.destroy()

    # def test_clients_get(self):

    #     # Create Account
    #     acct = self._create_account(self.acs, direct=True)

    #     # Test Get
    #     create_obj = functools.partial(self._create_client, direct=False)
    #     get_obj = functools.partial(acct.clients_get)
    #     self.helper_test_obj_existing(acct, accesscontrol.Client,
    #                                   create_obj, get_obj)

    #     # Cleanup
    #     acct.destroy()

    # def test_clients_list(self):

    #     # Create Account
    #     acct = self._create_account(self.acs, direct=True)

    #     # Test List
    #     create_obj = functools.partial(self._create_client, direct=False)
    #     list_objs = functools.partial(acct.clients_list)
    #     self.helper_test_objects_list(acct, accesscontrol.Client,
    #                                   create_obj, list_objs)

    #     # Cleanup
    #     acct.destroy()

    # def test_clients_exists(self):

    #     # Create Account
    #     acct = self._create_account(self.acs, direct=True)

    #     # Test Exists
    #     create_obj = functools.partial(self._create_client, direct=False)
    #     exists_obj = functools.partial(acct.clients_exists)
    #     self.helper_test_objects_exists(acct, accesscontrol.Client,
    #                                     create_obj, exists_obj)

    #     # Cleanup
    #     acct.destroy()

class ClientTestCase(AccessControlTestCase, ObjectsHelpers):

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


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
