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
import tutamen_server.accesscontrol

### Object Classes ###

class AccessControlTestCase(server_common.BaseTestCase):

    def create_accesscontrolserver(self):

        acs = tutamen_server.accesscontrol.AccessControlServer(self.driver)
        return acs

    def create_authorization_via_acs(self, acs):

        clientuid = uuid.uuid4()
        expiration = time.time()
        objperm = 'TESTPERM'
        objtype = 'TESTOBJ'
        objuid = uuid.uuid4()
        auth = acs.authorizations_create(clientuid=clientuid, expiration=expiration,
                                         objperm=objperm, objtype=objtype, objuid=objuid)
        return auth

class AccessControlServerTestCase(AccessControlTestCase):

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

    def test_init_and_destroy(self):

        # Create Server
        acs = self.create_accesscontrolserver()
        self.assertIsInstance(acs, tutamen_server.accesscontrol.AccessControlServer)

        # Cleanup
        acs.destroy()

    def test_authorizations_create(self):

        # Create Server
        acs = self.create_accesscontrolserver()

        # Create Authorization
        auth = self.create_authorization_via_acs(acs)
        self.assertIsInstance(auth, tutamen_server.accesscontrol.Authorization)
        self.assertTrue(auth.exists())

        # Cleanup
        auth.destroy()
        acs.destroy()

    def test_authorizations_get(self):

        # Create Server
        acs = self.create_accesscontrolserver()

        # Create Authorization
        auth = self.create_authorization_via_acs(acs)
        key = auth.key
        uid = auth.uid

        # Test get (key)
        auth = acs.authorizations_get(key=key)
        self.assertIsInstance(auth, tutamen_server.accesscontrol.Authorization)
        self.assertTrue(auth.exists())
        self.assertEqual(auth.key, key)
        self.assertEqual(auth.uid, uid)

        # Test get (uuid)
        auth = acs.authorizations_get(uid=uid)
        self.assertIsInstance(auth, tutamen_server.accesscontrol.Authorization)
        self.assertTrue(auth.exists())
        self.assertEqual(auth.key, key)
        self.assertEqual(auth.uid, uid)

        # Cleanup
        auth.destroy()
        acs.destroy()

    def test_authorizations_list(self):

        # Create Server
        acs = self.create_accesscontrolserver()

        # List Authorizations (Empty)
        keys = acs.authorizations_list()
        self.assertEqual(len(keys), 0)

        # Create Authorization
        auths = []
        for i in range(10):
            auths.append(self.create_authorization_via_acs(acs))

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
        acs = self.create_accesscontrolserver()

        # Test DNE (key)
        key = "fakekey"
        self.assertFalse(acs.authorizations_exists(key=key))

        # Test DNE (uuid)
        uid = uuid.uuid4()
        self.assertFalse(acs.authorizations_exists(uid=uid))

        # Create Authorization
        auth = self.create_authorization_via_acs(acs)
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


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
