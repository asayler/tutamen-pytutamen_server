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
from pytutamen_server import accesscontrol

### Object Classes ###

class AccessControlTestCase(tests_common.BaseTestCase):

    def _create_accesscontrolserver(self):

        acs = accesscontrol.AccessControlServer(self.driver)
        return acs

    def _create_authorization(self, acs, direct=False, **kwargs_user):

        clientuid = uuid.uuid4()
        expiration = time.time()
        objperm = 'TESTPERM'
        objtype = 'TESTOBJ'
        objuid = uuid.uuid4()
        kwargs = {'clientuid': clientuid, 'expiration': expiration,
                  'objperm': objperm, 'objtype': objtype, 'objuid': objuid}
        kwargs.update(kwargs_user)

        if direct:
            authorization = accesscontrol.Authorization(acs, create=True, **kwargs)
        else:
            authorization = acs.authorizations_create(**kwargs)
        return authorization

    def _create_verifier(self, acs, direct=False, **kwargs_user):

        kwargs = {}
        kwargs.update(kwargs_user)
        if direct:
            verifier = accesscontrol.Verifier(acs, create=True, **kwargs)
        else:
            verifier = acs.verifiers_create(**kwargs)
        return verifier

    def _create_authenticator(self, acs, direct=False, **kwargs_user):

        module = 'TESTMOD'
        kwargs = {'module': module}
        kwargs.update(kwargs_user)

        if direct:
            authenticator = accesscontrol.Authenticator(acs, create=True, **kwargs)
        else:
            authenticator = acs.authenticators_create(**kwargs)
        return authenticator

    def _create_account(self, acs, direct=False, **kwargs_user):

        kwargs = {}
        kwargs.update(kwargs_user)

        if direct:
            account = accesscontrol.Account(acs, create=True, **kwargs)
        else:
            account = acs.accounts_create(**kwargs)
        return account

    def _create_client(self, acct, direct=False, **kwargs_user):

        kwargs = {}
        kwargs.update(kwargs_user)

        if direct:
            client = accesscontrol.Client(acct, create=True, **kwargs)
        else:
            client = acct.clients_create(**kwargs)
        return client

class ObjectsHelpers(object):

    def helper_test_obj_create(self, srv, objtype, create_obj):

        # Create Object
        obj = create_obj(srv)
        self.assertIsInstance(obj, objtype)
        self.assertTrue(obj.exists())

        # Cleanup
        obj.destroy()

    def helper_test_obj_existing(self, srv, objtype, create_obj, get_obj):

        # Create Object
        obj = create_obj(srv)
        key = obj.key
        uid = obj.uid

        # Test get (key)
        obj = get_obj(key=key)
        self.assertIsInstance(obj, objtype)
        self.assertTrue(obj.exists())
        self.assertEqual(obj.key, key)
        self.assertEqual(obj.uid, uid)

        # Test get (uuid)
        obj = get_obj(uid=uid)
        self.assertIsInstance(obj, objtype)
        self.assertTrue(obj.exists())
        self.assertEqual(obj.key, key)
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

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

    ## Core Tests ##

    def test_init_and_destroy(self):

        # Create Server
        acs = self._create_accesscontrolserver()
        self.assertIsInstance(acs, accesscontrol.AccessControlServer)

        # Cleanup
        acs.destroy()

    ## Authorization Tests ##

    def test_authorizations_create(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Create
        create_obj = functools.partial(self._create_authorization, direct=False)
        self.helper_test_obj_create(acs, accesscontrol.Authorization,
                                    create_obj)

        # Cleanup
        acs.destroy()

    def test_authorizations_get(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Get
        create_obj = functools.partial(self._create_authorization, direct=False)
        get_obj = functools.partial(acs.authorizations_get)
        self.helper_test_obj_existing(acs, accesscontrol.Authorization,
                                      create_obj, get_obj)

        # Cleanup
        acs.destroy()

    def test_authorizations_list(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test List
        create_obj = functools.partial(self._create_authorization, direct=False)
        list_objs = functools.partial(acs.authorizations_list)
        self.helper_test_objects_list(acs, accesscontrol.Authorization,
                                      create_obj, list_objs)

        # Cleanup
        acs.destroy()

    def test_authorizations_exists(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Exists
        create_obj = functools.partial(self._create_authorization, direct=False)
        exists_obj = functools.partial(acs.authorizations_exists)
        self.helper_test_objects_exists(acs, accesscontrol.Authorization,
                                        create_obj, exists_obj)

        # Cleanup
        acs.destroy()

    ## Verifier Tests ##

    def test_verifiers_create(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Create
        create_obj = functools.partial(self._create_verifier, direct=False)
        self.helper_test_obj_create(acs, accesscontrol.Verifier,
                                    create_obj)

        # Cleanup
        acs.destroy()

    def test_verifiers_get(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Get
        create_obj = functools.partial(self._create_verifier, direct=False)
        get_obj = functools.partial(acs.verifiers_get)
        self.helper_test_obj_existing(acs, accesscontrol.Verifier,
                                      create_obj, get_obj)

        # Cleanup
        acs.destroy()

    def test_verifiers_list(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test List
        create_obj = functools.partial(self._create_verifier, direct=False)
        list_objs = functools.partial(acs.verifiers_list)
        self.helper_test_objects_list(acs, accesscontrol.Verifier,
                                      create_obj, list_objs)

        # Cleanup
        acs.destroy()

    def test_verifiers_exists(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Exists
        create_obj = functools.partial(self._create_verifier, direct=False)
        exists_obj = functools.partial(acs.verifiers_exists)
        self.helper_test_objects_exists(acs, accesscontrol.Verifier,
                                        create_obj, exists_obj)

        # Cleanup
        acs.destroy()

    ## Authenticator Tests ##

    def test_authenticators_create(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Create
        create_obj = functools.partial(self._create_authenticator, direct=False)
        self.helper_test_obj_create(acs, accesscontrol.Authenticator,
                                    create_obj)

        # Cleanup
        acs.destroy()

    def test_authenticators_get(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Get
        create_obj = functools.partial(self._create_authenticator, direct=False)
        get_obj = functools.partial(acs.authenticators_get)
        self.helper_test_obj_existing(acs, accesscontrol.Authenticator,
                                      create_obj, get_obj)

        # Cleanup
        acs.destroy()

    def test_authenticators_list(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test List
        create_obj = functools.partial(self._create_authenticator, direct=False)
        list_objs = functools.partial(acs.authenticators_list)
        self.helper_test_objects_list(acs, accesscontrol.Authenticator,
                                      create_obj, list_objs)

        # Cleanup
        acs.destroy()

    def test_authenticators_exists(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Exists
        create_obj = functools.partial(self._create_authenticator, direct=False)
        exists_obj = functools.partial(acs.authenticators_exists)
        self.helper_test_objects_exists(acs, accesscontrol.Authenticator,
                                        create_obj, exists_obj)

        # Cleanup
        acs.destroy()

    ## Account Tests ##

    def test_accounts_create(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Create
        create_obj = functools.partial(self._create_account, direct=False)
        self.helper_test_obj_create(acs, accesscontrol.Account,
                                    create_obj)

        # Cleanup
        acs.destroy()

    def test_accounts_get(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Get
        create_obj = functools.partial(self._create_account, direct=False)
        get_obj = functools.partial(acs.accounts_get)
        self.helper_test_obj_existing(acs, accesscontrol.Account,
                                      create_obj, get_obj)

        # Cleanup
        acs.destroy()

    def test_accounts_list(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test List
        create_obj = functools.partial(self._create_account, direct=False)
        list_objs = functools.partial(acs.accounts_list)
        self.helper_test_objects_list(acs, accesscontrol.Account,
                                      create_obj, list_objs)

        # Cleanup
        acs.destroy()

    def test_accounts_exists(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test Exists
        create_obj = functools.partial(self._create_account, direct=False)
        exists_obj = functools.partial(acs.accounts_exists)
        self.helper_test_objects_exists(acs, accesscontrol.Account,
                                        create_obj, exists_obj)

        # Cleanup
        acs.destroy()

class AuthorizationTestCase(AccessControlTestCase, ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver()

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_authorization, direct=True)
        self.helper_test_obj_create(self.acs, accesscontrol.Authorization,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_authorization, direct=True)
        get_obj = functools.partial(accesscontrol.Authorization, self.acs, create=False)
        self.helper_test_obj_existing(self.acs, accesscontrol.Authorization,
                                      create_obj, get_obj)

    def test_clientuid(self):

        # Create Authorization
        clientuid = uuid.uuid4()
        auth = self._create_authorization(self.acs, direct=True, clientuid=clientuid)

        # Test Client UID
        self.assertEqual(auth.clientuid, clientuid)

        # Cleanup
        auth.destroy()

    def test_expiration(self):

        # Create Authorization
        expiration = time.time()
        auth = self._create_authorization(self.acs, direct=True, expiration=expiration)

        # Test Expriation
        self.assertEqual(auth.expiration, expiration)

        # Cleanup
        auth.destroy()

    def test_objperm(self):

        # Create Authorization
        objperm = 'TESTPERM2'
        auth = self._create_authorization(self.acs, direct=True, objperm=objperm)

        # Test Expriation
        self.assertEqual(auth.objperm, objperm)

        # Cleanup
        auth.destroy()

    def test_objtype(self):

        # Create Authorization
        objtype = 'TESTOBJ'
        auth = self._create_authorization(self.acs, direct=True, objtype=objtype)

        # Test Expriation
        self.assertEqual(auth.objtype, objtype)

        # Cleanup
        auth.destroy()

    def test_objuid(self):

        # Create Authorization
        objuid = uuid.uuid4()
        auth = self._create_authorization(self.acs, direct=True, objuid=objuid)

        # Test Expriation
        self.assertEqual(auth.objuid, objuid)

        # Cleanup
        auth.destroy()

    def test_status(self):

        # Create Authorization
        auth = self._create_authorization(self.acs, direct=True)

        # Test Status
        self.assertEqual(auth.status, accesscontrol._NEW_STATUS)

        # Cleanup
        auth.destroy()

class VerifierTestCase(AccessControlTestCase, ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver()

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_verifier, direct=True)
        self.helper_test_obj_create(self.acs, accesscontrol.Verifier,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_verifier, direct=True)
        get_obj = functools.partial(accesscontrol.Verifier, self.acs, create=False)
        self.helper_test_obj_existing(self.acs, accesscontrol.Verifier,
                                      create_obj, get_obj)

    def test_authenticators_by_key(self):

        # Create Verifier
        verf = self._create_verifier(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(verf.authenticators_by_key()), 0)

        # Add to authenticators
        actr_objs = set()
        actr_keys = set()
        for i in range(10):
            actr = self._create_authenticator(self.acs)
            verf.authenticators_add(actr)
            actr_objs.add(actr)
            actr_keys.add(actr.key)

        # Test Full
        self.assertEqual(verf.authenticators_by_key(), actr_keys)

        # Remove Authenticators
        for actr in actr_objs:
            actr.destroy()

        # Test Empty
        self.assertEqual(len(verf.authenticators_by_key()), 0)

        # Cleanup
        verf.destroy()

    def test_authenticators_by_uid(self):

        # Create Verifier
        verf = self._create_verifier(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(verf.authenticators_by_uid()), 0)

        # Add to authenticators
        actr_objs = set()
        actr_uids = set()
        for i in range(10):
            actr = self._create_authenticator(self.acs)
            verf.authenticators_add(actr)
            actr_objs.add(actr)
            actr_uids.add(actr.uid)

        # Test Full
        self.assertEqual(verf.authenticators_by_uid(), actr_uids)

        # Remove Authenticators
        for actr in actr_objs:
            actr.destroy()

        # Test Empty
        self.assertEqual(len(verf.authenticators_by_uid()), 0)

        # Cleanup
        verf.destroy()

    def test_authenticators_by_obj(self):

        # Create Verifier
        verf = self._create_verifier(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(verf.authenticators_by_obj()), 0)

        # Add to authenticators
        actr_objs = set()
        for i in range(10):
            actr = self._create_authenticator(self.acs)
            verf.authenticators_add(actr)
            actr_objs.add(actr)

        # Test Full
        self.assertEqual(verf.authenticators_by_obj(), actr_objs)

        # Remove Authenticators
        for actr in actr_objs:
            actr.destroy()

        # Test Empty
        self.assertEqual(len(verf.authenticators_by_obj()), 0)

        # Cleanup
        verf.destroy()

    def test_authenticators_add_is_member(self):

        # Create Verifier and Authenticator
        verf = self._create_verifier(self.acs, direct=True)
        actr = self._create_authenticator(self.acs)

        # Test Add
        self.assertFalse(verf.authenticators_is_member(actr))
        self.assertFalse(verf in actr.verifiers_by_obj())
        verf.authenticators_add(actr)
        self.assertTrue(verf.authenticators_is_member(actr))
        self.assertTrue(verf in actr.verifiers_by_obj())

        # Cleanup
        actr.destroy()
        verf.destroy()

    def test_authenticators_remove_is_member(self):

        # Create Verifier and Authenticator
        verf = self._create_verifier(self.acs, direct=True)
        actr = self._create_authenticator(self.acs)
        verf.authenticators_add(actr)

        # Test Remove
        self.assertTrue(verf.authenticators_is_member(actr))
        self.assertTrue(verf in actr.verifiers_by_obj())
        verf.authenticators_remove(actr)
        self.assertFalse(verf.authenticators_is_member(actr))
        self.assertFalse(verf in actr.verifiers_by_obj())

        # Cleanup
        actr.destroy()
        verf.destroy()

    def test_accounts_by_key(self):

        # Create Verifier
        verf = self._create_verifier(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(verf.accounts_by_key()), 0)

        # Add to accounts
        acct_objs = set()
        acct_keys = set()
        for i in range(10):
            acct = self._create_account(self.acs)
            verf.accounts_add(acct)
            acct_objs.add(acct)
            acct_keys.add(acct.key)

        # Test Full
        self.assertEqual(verf.accounts_by_key(), acct_keys)

        # Remove Accounts
        for acct in acct_objs:
            acct.destroy()

        # Test Empty
        self.assertEqual(len(verf.accounts_by_key()), 0)

        # Cleanup
        verf.destroy()

    def test_accounts_by_uid(self):

        # Create Verifier
        verf = self._create_verifier(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(verf.accounts_by_uid()), 0)

        # Add to accounts
        acct_objs = set()
        acct_uids = set()
        for i in range(10):
            acct = self._create_account(self.acs)
            verf.accounts_add(acct)
            acct_objs.add(acct)
            acct_uids.add(acct.uid)

        # Test Full
        self.assertEqual(verf.accounts_by_uid(), acct_uids)

        # Remove Accounts
        for acct in acct_objs:
            acct.destroy()

        # Test Empty
        self.assertEqual(len(verf.accounts_by_uid()), 0)

        # Cleanup
        verf.destroy()

    def test_accounts_by_obj(self):

        # Create Verifier
        verf = self._create_verifier(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(verf.accounts_by_obj()), 0)

        # Add to accounts
        acct_objs = set()
        for i in range(10):
            acct = self._create_account(self.acs)
            verf.accounts_add(acct)
            acct_objs.add(acct)

        # Test Full
        self.assertEqual(verf.accounts_by_obj(), acct_objs)

        # Remove Accounts
        for acct in acct_objs:
            acct.destroy()

        # Test Empty
        self.assertEqual(len(verf.accounts_by_obj()), 0)

        # Cleanup
        verf.destroy()

    def test_accounts_add_is_member(self):

        # Create Verifier and Account
        verf = self._create_verifier(self.acs, direct=True)
        acct = self._create_account(self.acs)

        # Test Add
        self.assertFalse(verf.accounts_is_member(acct))
        self.assertFalse(verf in acct.verifiers_by_obj())
        verf.accounts_add(acct)
        self.assertTrue(verf.accounts_is_member(acct))
        self.assertTrue(verf in acct.verifiers_by_obj())

        # Cleanup
        acct.destroy()
        verf.destroy()

    def test_accounts_remove_is_member(self):

        # Create Verifier and Account
        verf = self._create_verifier(self.acs, direct=True)
        acct = self._create_account(self.acs)
        verf.accounts_add(acct)

        # Test Remove
        self.assertTrue(verf.accounts_is_member(acct))
        self.assertTrue(verf in acct.verifiers_by_obj())
        verf.accounts_remove(acct)
        self.assertFalse(verf.accounts_is_member(acct))
        self.assertFalse(verf in acct.verifiers_by_obj())

        # Cleanup
        acct.destroy()
        verf.destroy()

class AuthenticatorTestCase(AccessControlTestCase, ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver()

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_authenticator, direct=True)
        self.helper_test_obj_create(self.acs, accesscontrol.Authenticator,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_authenticator, direct=True)
        get_obj = functools.partial(accesscontrol.Authenticator, self.acs, create=False)
        self.helper_test_obj_existing(self.acs, accesscontrol.Authenticator,
                                      create_obj, get_obj)

    def test_module(self):

        # Create Authenticator
        module = 'TESTMODULE'
        auth = self._create_authenticator(self.acs, direct=True, module=module)

        # Test Client UID
        self.assertEqual(auth.module, module)

        # Cleanup
        auth.destroy()

    def test_verifiers_by_key(self):

        # Create Authenticator
        actr = self._create_authenticator(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(actr.verifiers_by_key()), 0)

        # Add to verifiers
        verifier_objs = set()
        verifier_keys = set()
        for i in range(10):
            verifier = self._create_verifier(self.acs)
            verifier.authenticators_add(actr)
            verifier_objs.add(verifier)
            verifier_keys.add(verifier.key)

        # Test Full
        self.assertEqual(actr.verifiers_by_key(), verifier_keys)

        # Remove Verifiers
        for verifier in verifier_objs:
            verifier.destroy()

        # Test Empty
        self.assertEqual(len(actr.verifiers_by_key()), 0)

        # Cleanup
        actr.destroy()

    def test_verifiers_by_uid(self):

        # Create Authenticator
        actr = self._create_authenticator(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(actr.verifiers_by_uid()), 0)

        # Add Verifiers
        verifier_objs = set()
        verifier_uids = set()
        for i in range(10):
            verifier = self._create_verifier(self.acs)
            verifier.authenticators_add(actr)
            verifier_objs.add(verifier)
            verifier_uids.add(verifier.uid)

        # Test Full
        self.assertEqual(actr.verifiers_by_uid(), verifier_uids)

        # Remove Verifiers
        for verifier in verifier_objs:
            verifier.destroy()

        # Test Empty
        self.assertEqual(len(actr.verifiers_by_uid()), 0)

        # Cleanup
        actr.destroy()

    def test_verifiers_by_obj(self):

        # Create Authenticator
        actr = self._create_authenticator(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(actr.verifiers_by_obj()), 0)

        # Add Verifiers
        verifier_objs = set()
        for i in range(10):
            verifier = self._create_verifier(self.acs)
            verifier.authenticators_add(actr)
            verifier_objs.add(verifier)

        # Test Full
        self.assertEqual(actr.verifiers_by_obj(), verifier_objs)

        # Remove Verifiers
        for verifier in verifier_objs:
            verifier.destroy()

        # Test Empty
        self.assertEqual(len(actr.verifiers_by_obj()), 0)

        # Cleanup
        actr.destroy()

class AccountTestCase(AccessControlTestCase, ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver()

    def tearDown(self):

        # Teardown Properties
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_account, direct=True)
        self.helper_test_obj_create(self.acs, accesscontrol.Account,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_account, direct=True)
        get_obj = functools.partial(accesscontrol.Account, self.acs, create=False)
        self.helper_test_obj_existing(self.acs, accesscontrol.Account,
                                      create_obj, get_obj)

    def test_verifiers_by_key(self):

        # Create Account
        acct = self._create_account(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(acct.verifiers_by_key()), 0)

        # Add to verifiers
        verifier_objs = set()
        verifier_keys = set()
        for i in range(10):
            verifier = self._create_verifier(self.acs)
            verifier.accounts_add(acct)
            verifier_objs.add(verifier)
            verifier_keys.add(verifier.key)

        # Test Full
        self.assertEqual(acct.verifiers_by_key(), verifier_keys)

        # Remove Verifiers
        for verifier in verifier_objs:
            verifier.destroy()

        # Test Empty
        self.assertEqual(len(acct.verifiers_by_key()), 0)

        # Cleanup
        acct.destroy()

    def test_verifiers_by_uid(self):

        # Create Account
        acct = self._create_account(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(acct.verifiers_by_uid()), 0)

        # Add Verifiers
        verifier_objs = set()
        verifier_uids = set()
        for i in range(10):
            verifier = self._create_verifier(self.acs)
            verifier.accounts_add(acct)
            verifier_objs.add(verifier)
            verifier_uids.add(verifier.uid)

        # Test Full
        self.assertEqual(acct.verifiers_by_uid(), verifier_uids)

        # Remove Verifiers
        for verifier in verifier_objs:
            verifier.destroy()

        # Test Empty
        self.assertEqual(len(acct.verifiers_by_uid()), 0)

        # Cleanup
        acct.destroy()

    def test_verifiers_by_obj(self):

        # Create Account
        acct = self._create_account(self.acs, direct=True)

        # Test Empty
        self.assertEqual(len(acct.verifiers_by_obj()), 0)

        # Add Verifiers
        verifier_objs = set()
        for i in range(10):
            verifier = self._create_verifier(self.acs)
            verifier.accounts_add(acct)
            verifier_objs.add(verifier)

        # Test Full
        self.assertEqual(acct.verifiers_by_obj(), verifier_objs)

        # Remove Verifiers
        for verifier in verifier_objs:
            verifier.destroy()

        # Test Empty
        self.assertEqual(len(acct.verifiers_by_obj()), 0)

        # Cleanup
        acct.destroy()

    ## Client Tests ##

    def test_clients_create(self):

        # Create Account
        acct = self._create_account(self.acs, direct=True)

        # Test Create
        create_obj = functools.partial(self._create_client, direct=False)
        self.helper_test_obj_create(acct, accesscontrol.Client,
                                    create_obj)

        # Cleanup
        acct.destroy()

    def test_clients_get(self):

        # Create Account
        acct = self._create_account(self.acs, direct=True)

        # Test Get
        create_obj = functools.partial(self._create_client, direct=False)
        get_obj = functools.partial(acct.clients_get)
        self.helper_test_obj_existing(acct, accesscontrol.Client,
                                      create_obj, get_obj)

        # Cleanup
        acct.destroy()

    def test_clients_list(self):

        # Create Account
        acct = self._create_account(self.acs, direct=True)

        # Test List
        create_obj = functools.partial(self._create_client, direct=False)
        list_objs = functools.partial(acct.clients_list)
        self.helper_test_objects_list(acct, accesscontrol.Client,
                                      create_obj, list_objs)

        # Cleanup
        acct.destroy()

    def test_clients_exists(self):

        # Create Account
        acct = self._create_account(self.acs, direct=True)

        # Test Exists
        create_obj = functools.partial(self._create_client, direct=False)
        exists_obj = functools.partial(acct.clients_exists)
        self.helper_test_objects_exists(acct, accesscontrol.Client,
                                        create_obj, exists_obj)

        # Cleanup
        acct.destroy()

class ClientTestCase(AccessControlTestCase, ObjectsHelpers):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.acs = self._create_accesscontrolserver()
        self.acct = self._create_account(self.acs)

    def tearDown(self):

        # Teardown Properties
        self.acct.destroy()
        self.acs.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        create_obj = functools.partial(self._create_client, direct=True)
        self.helper_test_obj_create(self.acct, accesscontrol.Client,
                                    create_obj)

    def test_init_existing(self):

        create_obj = functools.partial(self._create_client, direct=True)
        get_obj = functools.partial(accesscontrol.Client, self.acct, create=False)
        self.helper_test_obj_existing(self.acct, accesscontrol.Client,
                                      create_obj, get_obj)

    def test_account(self):

        # Create Client
        client = self._create_client(self.acct, direct=True)

        # Test Account
        self.assertEqual(client.account, self.acct)

        # Cleanup
        client.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
