#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Access Control Tests


### Imports ###

## stdlib ##
import time
import uuid
import unittest

# Tests Common
import server_common

## tutamen_server ##
from tutamen_server import accesscontrol

### Object Classes ###

class AccessControlTestCase(server_common.BaseTestCase):

    def _create_accesscontrolserver(self):

        acs = accesscontrol.AccessControlServer(self.driver)
        return acs

    def _get_authorization_kwargs(self):

        clientuid = uuid.uuid4()
        expiration = time.time()
        objperm = 'TESTPERM'
        objtype = 'TESTOBJ'
        objuid = uuid.uuid4()
        return {'clientuid': clientuid, 'expiration': expiration,
                'objperm': objperm, 'objtype': objtype, 'objuid': objuid}

    def _create_authorization_via_acs(self, acs, **kwargs_user):

        kwargs = self._get_authorization_kwargs()
        kwargs.update(kwargs_user)
        auth = acs.authorizations_create(**kwargs)
        return auth

    def _create_authorization(self, acs, **kwargs_user):

        kwargs = self._get_authorization_kwargs()
        kwargs.update(kwargs_user)
        auth = accesscontrol.Authorization(acs, create=True, **kwargs)
        return auth

class AccessControlServerTestCase(AccessControlTestCase):

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

    def test_init_and_destroy(self):

        # Create Server
        acs = self._create_accesscontrolserver()
        self.assertIsInstance(acs, accesscontrol.AccessControlServer)

        # Cleanup
        acs.destroy()

    def test_authorizations_create(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Create Authorization
        auth = self._create_authorization_via_acs(acs)
        self.assertIsInstance(auth, accesscontrol.Authorization)
        self.assertTrue(auth.exists())

        # Cleanup
        auth.destroy()
        acs.destroy()

    def test_authorizations_get(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Create Authorization
        auth = self._create_authorization_via_acs(acs)
        key = auth.key
        uid = auth.uid

        # Test get (key)
        auth = acs.authorizations_get(key=key)
        self.assertIsInstance(auth, accesscontrol.Authorization)
        self.assertTrue(auth.exists())
        self.assertEqual(auth.key, key)
        self.assertEqual(auth.uid, uid)

        # Test get (uuid)
        auth = acs.authorizations_get(uid=uid)
        self.assertIsInstance(auth, accesscontrol.Authorization)
        self.assertTrue(auth.exists())
        self.assertEqual(auth.key, key)
        self.assertEqual(auth.uid, uid)

        # Cleanup
        auth.destroy()
        acs.destroy()

    def test_authorizations_list(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # List Authorizations (Empty)
        keys = acs.authorizations_list()
        self.assertEqual(len(keys), 0)

        # Create Authorization
        auths = []
        for i in range(10):
            auths.append(self._create_authorization_via_acs(acs))

        # List Authorizations (Full)
        keys = acs.authorizations_list()
        self.assertEqual(len(keys), len(auths))
        for auth in auths:
            self.assertTrue(auth.key in keys)

        # Delete Authorizations
        for auth in auths:
            auth.destroy()

        # List Authorizations (Empty)
        keys = acs.authorizations_list()
        self.assertEqual(len(keys), 0)

        # Cleanup
        acs.destroy()

    def test_authorizations_exists(self):

        # Create Server
        acs = self._create_accesscontrolserver()

        # Test DNE (key)
        key = "fakekey"
        self.assertFalse(acs.authorizations_exists(key=key))

        # Test DNE (uuid)
        uid = uuid.uuid4()
        self.assertFalse(acs.authorizations_exists(uid=uid))

        # Create Authorization
        auth = self._create_authorization_via_acs(acs)
        key = auth.key
        uid = auth.uid

        # Test Exists (key)
        self.assertTrue(acs.authorizations_exists(key=key))

        # Test Exists (uuid)
        self.assertTrue(acs.authorizations_exists(uid=uid))

        # Delete Authorization
        auth.destroy()

        # Test DNE (key)
        self.assertFalse(acs.authorizations_exists(key=key))

        # Test DNE (uuid)
        self.assertFalse(acs.authorizations_exists(uid=uid))

        # Cleanup
        acs.destroy()

class AuthorizationTestCase(AccessControlTestCase):

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

        # Test Create
        auth = self._create_authorization(self.acs)
        self.assertIsInstance(auth, accesscontrol.Authorization)
        self.assertTrue(auth.exists())

        # Cleanup
        auth.destroy()

    def test_init_existing(self):

        # Create Authorization
        auth = self._create_authorization(self.acs)
        key = auth.key
        uid = auth.uid

        # Test get (key)
        auth = accesscontrol.Authorization(self.acs, create=False, key=key)
        self.assertIsInstance(auth, accesscontrol.Authorization)
        self.assertTrue(auth.exists())
        self.assertEqual(auth.key, key)
        self.assertEqual(auth.uid, uid)

        # Test get (uuid)
        auth = accesscontrol.Authorization(self.acs, create=False, uid=uid)
        self.assertIsInstance(auth, accesscontrol.Authorization)
        self.assertTrue(auth.exists())
        self.assertEqual(auth.key, key)
        self.assertEqual(auth.uid, uid)

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

        # Test Expriation
        self.assertEqual(auth.status, accesscontrol._NEW_STATUS)

        # Cleanup
        auth.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
