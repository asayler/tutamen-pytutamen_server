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

class CollectionTestCase(server_common.BaseTestCase):

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

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.ss = tutamen_server.storage.StorageServer(self.driver)
        self.col = self.ss.collections_create()

    def tearDown(self):

        # Teardown Properties
        self.col.destroy()
        self.ss.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        # Test Create
        sec = tutamen_server.storage.Secret(self.col, create=True)
        self.assertIsInstance(sec, tutamen_server.storage.Secret)
        self.assertTrue(sec.exists())

        # Cleanup
        sec.destroy()

    def test_init_existing(self):

        # Create Secret
        sec = tutamen_server.storage.Secret(self.col, create=True)
        key = sec.key
        uid = sec.uid

        # Test get (key)
        sec = tutamen_server.storage.Secret(self.col, create=False, key=key)
        self.assertIsInstance(sec, tutamen_server.storage.Secret)
        self.assertTrue(sec.exists())
        self.assertEqual(sec.key, key)
        self.assertEqual(sec.uid, uid)

        # Test get (uuid)
        sec = tutamen_server.storage.Secret(self.col, create=False, uid=uid)
        self.assertIsInstance(sec, tutamen_server.storage.Secret)
        self.assertTrue(sec.exists())
        self.assertEqual(sec.key, key)
        self.assertEqual(sec.uid, uid)

        # Cleanup
        sec.destroy()

    def test_collection(self):

        # Create Collection
        sec = tutamen_server.storage.Secret(self.col, create=True)

        # Test Metadata
        self.assertEqual(sec.collection, self.col)

        # Cleanup
        sec.destroy()

    def test_metadata(self):

        # Create Collection
        metadata = {"key1": "val1", "key2": "val2", "key3": "val3"}
        sec = tutamen_server.storage.Secret(self.col, create=True, metadata=metadata)

        # Test Metadata
        self.assertEqual(sec.metadata, metadata)

        # Cleanup
        sec.destroy()

    def test_data(self):

        # Create Collection
        data = '''
-----BEGIN FAKE RSA PRIVATE KEY-----
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
-----END FAKE RSA PRIVATE KEY-----
'''
        sec = tutamen_server.storage.Secret(self.col, create=True, data=data)

        # Test Metadata
        self.assertEqual(sec.data, data)

        # Cleanup
        sec.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
