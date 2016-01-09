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

    def helper_test_master_obj_index(self, create_master, create_slave,
                                     get_master_index):

        # Create Master Obj
        master = create_master()

        # Test Empty
        self.assertEqual(len(get_master_index(master)), 0)
        self.assertEqual(get_master_index(master).by_obj(), set())

        # Create Slaves
        slaves = set()
        for i in range(10):
            slave = create_slave()
            slaves.add(slave)

        # Add Slaves
        for slave in slaves:
            get_master_index(master).add(slave)
            self.assertTrue(get_master_index(master).ismember(slave))

        # Test Full
        self.assertEqual(len(get_master_index(master)), 10)
        self.assertEqual(get_master_index(master).by_obj(), slaves)

        # Remove some slaves
        rem_slaves = set()
        for slave in slaves:
            get_master_index(master).remove(slave)
            self.assertFalse(get_master_index(master).ismember(slave))
            rem_slaves.add(slave)
            if len(rem_slaves) >= 5:
                break
        self.assertEqual(len(get_master_index(master)), 5)
        self.assertEqual(get_master_index(master).by_obj(), (slaves - rem_slaves))

        # Cleanup Slaves
        for slave in slaves:
            slave.destroy()

        # Test Empty
        self.assertEqual(len(get_master_index(master)), 0)
        self.assertEqual(get_master_index(master).by_obj(), set())

        # Cleanup
        master.destroy()

    def helper_test_slave_obj_index(self, create_master, create_slave,
                                    get_master_index, get_slave_index):

        # Create Slave Obj
        slave = create_slave()

        # Test Empty
        self.assertEqual(len(get_slave_index(slave)), 0)
        self.assertEqual(get_slave_index(slave).by_obj(), set())

        # Create Master
        masters = set()
        for i in range(10):
            master = create_master()
            masters.add(master)

        # Add Masters
        for master in masters:
            get_master_index(master).add(slave)
            self.assertTrue(get_slave_index(slave).ismember(master))

        # Test Full
        self.assertEqual(len(get_slave_index(slave)), 10)
        self.assertEqual(get_slave_index(slave).by_obj(), masters)

        # Remove some masters
        rem_masters = set()
        for master in masters:
            get_master_index(master).remove(slave)
            self.assertFalse(get_slave_index(slave).ismember(master))
            rem_masters.add(master)
            if len(rem_masters) >= 5:
                break
        self.assertEqual(len(get_slave_index(slave)), 5)
        self.assertEqual(get_slave_index(slave).by_obj(), (masters - rem_masters))

        # Cleanup Masters
        for master in masters:
            master.destroy()

        # Test Empty
        self.assertEqual(len(get_slave_index(slave)), 0)
        self.assertEqual(get_slave_index(slave).by_obj(), set())

        # Cleanup
        slave.destroy()

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
