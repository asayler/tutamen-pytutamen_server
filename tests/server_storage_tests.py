#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Storage Tests


### Imports ###

## stdlib ##
import unittest
import uuid

# Tests Common
import server_common

## tutamen_server ##
import tutamen_server.storage


### Object Classes ###

class StorageServerTestCase(server_common.BaseTestCase):

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

    def test_init_and_destroy(self):

        # Create Server
        ss = tutamen_server.storage.StorageServer(self.driver)
        self.assertIsInstance(ss, tutamen_server.storage.StorageServer)

        # Cleanup
        ss.destroy()

    def test_collections_create(self):

        # Create Server
        ss = tutamen_server.storage.StorageServer(self.driver)

        # Create Collection
        col = ss.collections_create()
        self.assertIsInstance(col, tutamen_server.storage.Collection)
        self.assertTrue(col.exists())

        # Cleanup
        col.destroy()
        ss.destroy()

    def test_collections_get(self):

        # Create Server
        ss = tutamen_server.storage.StorageServer(self.driver)

        # Create Collection
        col = ss.collections_create()
        key = col.key
        uid = col.uuid

        # Test get (key)
        col = ss.collections_get(key=key)
        self.assertIsInstance(col, tutamen_server.storage.Collection)
        self.assertTrue(col.exists())

        # Test get (uuid)
        col = ss.collections_get(uid=uid)
        self.assertIsInstance(col, tutamen_server.storage.Collection)
        self.assertTrue(col.exists())

        # Cleanup
        col.destroy()
        ss.destroy()

    def test_collections_list(self):

        # Create Server
        ss = tutamen_server.storage.StorageServer(self.driver)

        # List Collections (Empty)
        keys = ss.collections_list()
        self.assertEqual(len(keys), 0)

        # Create Collection
        cols = []
        for i in range(10):
            cols.append(ss.collections_create())

        # List Collections (Full)
        keys = ss.collections_list()
        self.assertEqual(len(keys), len(cols))
        for col in cols:
            self.assertTrue(col.key in keys)

        # Delete Collections
        for col in cols:
            col.destroy()

        # List Collections (Empty)
        keys = ss.collections_list()
        self.assertEqual(len(keys), 0)

        # Cleanup
        ss.destroy()

    def test_collections_exists(self):

        # Create Server
        ss = tutamen_server.storage.StorageServer(self.driver)

        # Test DNE (key)
        key = "fakekey"
        self.assertFalse(ss.collections_exists(key=key))

        # Test DNE (uuid)
        uid = uuid.uuid4()
        self.assertFalse(ss.collections_exists(uid=uid))

        # Create Collection
        col = ss.collections_create()
        key = col.key
        uid = col.uuid

        # Test Exists (key)
        self.assertTrue(ss.collections_exists(key=key))

        # Test Exists (uuid)
        self.assertTrue(ss.collections_exists(uid=uid))

        # Delete Collection
        col.destroy()

        # Test DNE
        self.assertFalse(ss.collections_exists(key=key))

        # Cleanup
        ss.destroy()

class SecretTestCase(server_common.BaseTestCase):

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.ss = tutamen_server.storage.StorageServer(self.driver)

    def tearDown(self):

        # Teardown Properties
        self.ss.wipe()

        # Call Parent
        super().tearDown()

    def test_from_new(self):

        # Create
        data = "Test Data"
        sec = self.ss.secret_from_new(data)

        # Test
        self.assertIsNotNone(sec)
        self.assertIsInstance(sec, tutamen_server.storage.Secret)

        # Cleanup
        sec.rem()

    def test_from_existing(self):

        # Create
        data = "Test Data"
        uid = self.ss.secret_from_new(data).uid
        sec = self.ss.secret_from_existing(uid)

        # Test
        self.assertIsNotNone(sec)
        self.assertIsInstance(sec, tutamen_server.storage.Secret)

        # Cleanup
        sec.rem()

    def test_uid(self):

        # Create Secret
        data = "Test Data"
        uid = self.ss.secret_from_new(data).uid
        sec = self.ss.secret_from_existing(uid)

        # Test
        self.assertEqual(uid, sec.uid)

        # Cleanup
        sec.rem()

    def test_data(self):

        # Create
        data = "Test Data"
        sec = self.ss.secret_from_new(data)

        # Test
        self.assertEqual(data, sec.data)

        # Cleanup
        sec.rem()

    def test_exists(self):

        # Create
        data = "Test Data"
        sec = self.ss.secret_from_new(data)

        # Test Exists
        self.assertTrue(sec.exists())

        # Cleanup
        sec.rem()

        # Test Not Exists
        self.assertFalse(sec.exists())


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
