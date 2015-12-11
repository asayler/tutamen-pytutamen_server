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
        uid = col.uid

        # Test get (key)
        col = ss.collections_get(key=key)
        self.assertIsInstance(col, tutamen_server.storage.Collection)
        self.assertTrue(col.exists())
        self.assertEqual(col.key, key)
        self.assertEqual(col.uid, uid)

        # Test get (uuid)
        col = ss.collections_get(uid=uid)
        self.assertIsInstance(col, tutamen_server.storage.Collection)
        self.assertTrue(col.exists())
        self.assertEqual(col.key, key)
        self.assertEqual(col.uid, uid)

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
        uid = col.uid

        # Test Exists (key)
        self.assertTrue(ss.collections_exists(key=key))

        # Test Exists (uuid)
        self.assertTrue(ss.collections_exists(uid=uid))

        # Delete Collection
        col.destroy()

        # Test DNE (key)
        self.assertFalse(ss.collections_exists(key=key))

        # Test DNE (uuid)
        self.assertFalse(ss.collections_exists(uid=uid))

        # Cleanup
        ss.destroy()

class StorageObjectTestBasis(server_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.ss = tutamen_server.storage.StorageServer(self.driver)

    def tearDown(self):

        # Teardown Properties
        self.ss.destroy()

        # Call Parent
        super().tearDown()

class CollectionTestCase(StorageObjectTestBasis):

    def test_init_create(self):

        # Test Create
        col = tutamen_server.storage.Collection(self.ss, create=True)
        self.assertIsInstance(col, tutamen_server.storage.Collection)
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections_exists(key=col.key))
        self.assertIn(col.key, self.ss.collections_list())

        # Cleanup
        col.destroy()

    def test_init_existing(self):

        # Create Collection
        col = tutamen_server.storage.Collection(self.ss, create=True)
        key = col.key
        uid = col.uid

        # Test get (key)
        col = tutamen_server.storage.Collection(self.ss, create=False, key=key)
        self.assertIsInstance(col, tutamen_server.storage.Collection)
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections_exists(key=col.key))
        self.assertIn(col.key, self.ss.collections_list())
        self.assertEqual(col.key, key)
        self.assertEqual(col.uid, uid)

        # Test get (uuid)
        col = tutamen_server.storage.Collection(self.ss, create=False, uid=uid)
        self.assertIsInstance(col, tutamen_server.storage.Collection)
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections_exists(key=col.key))
        self.assertIn(col.key, self.ss.collections_list())
        self.assertEqual(col.key, key)
        self.assertEqual(col.uid, uid)

        # Cleanup
        col.destroy()

    def test_destroy(self):

        # Create Collection
        col = tutamen_server.storage.Collection(self.ss, create=True)

        # Test Destroy
        col.destroy()
        self.assertFalse(col.exists())
        self.assertFalse(self.ss.collections_exists(key=col.key))
        self.assertNotIn(col.key, self.ss.collections_list())

    def test_metadata(self):

        # Create Collection
        metadata = {"key1": "val1", "key2": "val2", "key3": "val3"}
        col = tutamen_server.storage.Collection(self.ss, create=True, metadata=metadata)

        # Test Metadata
        self.assertEqual(col.metadata, metadata)

        # Cleanup
        col.destroy()

    def test_secrets_create(self):

        # Create Collection
        col = tutamen_server.storage.Collection(self.ss, create=True)

        # Create Secret
        sec = col.secrets_create()
        self.assertIsInstance(sec, tutamen_server.storage.Secret)
        self.assertTrue(sec.exists())

        # Cleanup
        sec.destroy()
        col.destroy()

    def test_secrets_get(self):

        # Create Collection
        col = tutamen_server.storage.Collection(self.ss, create=True)

        # Create Secret
        sec = col.secrets_create()
        key = sec.key
        uid = sec.uid

        # Test get (key)
        sec = col.secrets_get(key=key)
        self.assertIsInstance(sec, tutamen_server.storage.Secret)
        self.assertTrue(sec.exists())
        self.assertEqual(sec.key, key)
        self.assertEqual(sec.uid, uid)

        # Test get (uuid)
        sec = col.secrets_get(uid=uid)
        self.assertIsInstance(sec, tutamen_server.storage.Secret)
        self.assertTrue(sec.exists())
        self.assertEqual(sec.key, key)
        self.assertEqual(sec.uid, uid)

        # Cleanup
        sec.destroy()
        col.destroy()

    def test_secrets_list(self):

        # Create Collection
        col = tutamen_server.storage.Collection(self.ss, create=True)

        # List Secrets (Empty)
        keys = col.secrets_list()
        self.assertEqual(len(keys), 0)

        # Create Secret
        secs = []
        for i in range(10):
            secs.append(col.secrets_create())

        # List Secrets (Full)
        keys = col.secrets_list()
        self.assertEqual(len(keys), len(secs))
        for sec in secs:
            self.assertTrue(sec.key in keys)

        # Delete Secrets
        for sec in secs:
            sec.destroy()

        # List Secrets (Empty)
        keys = col.secrets_list()
        self.assertEqual(len(keys), 0)

        # Cleanup
        col.destroy()

    def test_secrets_exists(self):

        # Create Collection
        col = tutamen_server.storage.Collection(self.ss, create=True)

        # Test DNE (key)
        key = "fakekey"
        self.assertFalse(col.secrets_exists(key=key))

        # Test DNE (uuid)
        uid = uuid.uuid4()
        self.assertFalse(col.secrets_exists(uid=uid))

        # Create Secret
        sec = col.secrets_create()
        key = sec.key
        uid = sec.uid

        # Test Exists (key)
        self.assertTrue(col.secrets_exists(key=key))

        # Test Exists (uuid)
        self.assertTrue(col.secrets_exists(uid=uid))

        # Delete Secret
        sec.destroy()

        # Test DNE (key)
        self.assertFalse(col.secrets_exists(key=key))

        # Test DNE (uuid)
        self.assertFalse(col.secrets_exists(uid=uid))

        # Cleanup
        col.destroy()

class SecretTestCase(server_common.BaseTestCase):

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
