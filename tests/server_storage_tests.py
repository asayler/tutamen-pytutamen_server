#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Storage Tests


### Imports ###

## stdlib ##
import unittest
import uuid

## Tests Common ##
import tests_common

## pcollections ##
from pcollections import collections
from pcollections import abc_base

## tutamen_server ##
from pytutamen_server import datatypes
from pytutamen_server import storage


### Object Classes ###

class StorageServerTestCase(tests_common.BaseTestCase):

    def test_init_and_destroy(self):

        # Create Server
        ss = storage.StorageServer(self.pbackend)
        self.assertIsInstance(ss, storage.StorageServer)

        # Cleanup
        ss.destroy()

    def test_collections(self):

        # Create Server
        ss = storage.StorageServer(self.pbackend)

        # Test Collections
        self.assertIsInstance(ss.collections, datatypes.ChildIndex)
        self.assertEqual(ss.collections.type_child, storage.Collection)
        self.assertEqual(ss.collections.parent, ss)

        # Cleanup
        ss.destroy()

class CollectionTestCase(tests_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.ss = storage.StorageServer(self.pbackend)

    def tearDown(self):

        # Teardown Properties
        self.ss.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        # Test Create (Random)
        col = self.ss.collections.create()
        self.assertIsInstance(col, storage.Collection)
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections.exists(col))
        col.destroy()

        # Test Create (Key)
        key = "eb424026-6f54-4ef8-a4d0-bb658a1fc6cf"
        col = self.ss.collections.create(key=key)
        self.assertIsInstance(col, storage.Collection)
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections.exists(col))
        self.assertEqual(col.key, key)
        col.destroy()

        # Test Create (UID)
        uid = uuid.uuid4()
        col = self.ss.collections.create(uid=uid)
        self.assertIsInstance(col, storage.Collection)
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections.exists(col))
        self.assertEqual(col.uid, uid)
        col.destroy()

    def test_init_existing(self):

        # Test DNE
        uid = uuid.uuid4()
        self.assertRaises(datatypes.ObjectDNE, self.ss.collections.get, uid=uid)

        # Create Collection
        col = self.ss.collections.create()
        key = col.key
        uid = col.uid

        # Test get (key)
        col = self.ss.collections.get(key=key)
        self.assertIsInstance(col, storage.Collection)
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections.exists(col))
        self.assertEqual(col.key, key)

        # Test get (uuid)
        col = self.ss.collections.get(uid=uid)
        self.assertIsInstance(col, storage.Collection)
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections.exists(col))
        self.assertEqual(col.uid, uid)

        # Cleanup
        col.destroy()

    def test_destroy(self):

        # Create Collection
        col = self.ss.collections.create()
        self.assertTrue(col.exists())
        self.assertTrue(self.ss.collections.exists(col))

        # Test Destroy
        col.destroy()
        self.assertFalse(col.exists())
        self.assertFalse(self.ss.collections.exists(col))

    def test_userdata(self):

        # Create Collection
        userdata = {"key1": "val1", "key2": "val2", "key3": "val3"}
        col = self.ss.collections.create(userdata=userdata)

        # Test Metadata
        self.assertEqual(col.userdata, userdata)

        # Cleanup
        col.destroy()

    def test_server(self):

        # Create Collection
        col = self.ss.collections.create()

        # Test Server
        self.assertEqual(col.server, self.ss)

        # Cleanup
        col.destroy()

    def test_secrets(self):

        # Create Collection
        col = self.ss.collections.create()

        # Test Secrets
        self.assertIsInstance(col.secrets, datatypes.ChildIndex)
        self.assertEqual(col.secrets.type_child, storage.Secret)
        self.assertEqual(col.secrets.parent, col)

        # Cleanup
        col.destroy()

class SecretTestCase(tests_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.ss = storage.StorageServer(self.pbackend)
        self.col = self.ss.collections.create()

    def tearDown(self):

        # Teardown Properties
        self.col.destroy()
        self.ss.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create(self):

        # Test Create (Random)
        sec = self.col.secrets.create()
        self.assertIsInstance(sec, storage.Secret)
        self.assertTrue(sec.exists())
        self.assertTrue(self.col.secrets.exists(sec))
        sec.destroy()

        # Test Create (Key)
        key = "eb424026-6f54-4ef8-a4d0-bb658a1fc6cf"
        sec = self.col.secrets.create(key=key)
        self.assertIsInstance(sec, storage.Secret)
        self.assertTrue(sec.exists())
        self.assertTrue(self.col.secrets.exists(sec))
        self.assertEqual(sec.key, key)
        sec.destroy()

        # Test Create (UID)
        uid = uuid.uuid4()
        sec = self.col.secrets.create(uid=uid)
        self.assertIsInstance(sec, storage.Secret)
        self.assertTrue(sec.exists())
        self.assertTrue(self.col.secrets.exists(sec))
        self.assertEqual(sec.uid, uid)
        sec.destroy()

    def test_init_existing(self):

        # Test DNE
        uid = uuid.uuid4()
        self.assertRaises(datatypes.ObjectDNE, self.col.secrets.get, uid=uid)

        # Create Secret
        sec = self.col.secrets.create()
        key = sec.key
        uid = sec.uid

        # Test get (key)
        sec = self.col.secrets.get(key=key)
        self.assertIsInstance(sec, storage.Secret)
        self.assertTrue(sec.exists())
        self.assertTrue(self.col.secrets.exists(sec))
        self.assertEqual(sec.key, key)

        # Test get (uuid)
        sec = self.col.secrets.get(uid=uid)
        self.assertIsInstance(sec, storage.Secret)
        self.assertTrue(sec.exists())
        self.assertTrue(self.col.secrets.exists(sec))
        self.assertEqual(sec.uid, uid)

        # Cleanup
        sec.destroy()

    def test_server(self):

        # Create Secret
        sec = self.col.secrets.create()

        # Test Server
        self.assertEqual(sec.server, self.ss)

        # Cleanup
        sec.destroy()

    def test_collection(self):

        # Create Secret
        sec = self.col.secrets.create()

        # Test Collections
        self.assertEqual(sec.collection, self.col)

        # Cleanup
        sec.destroy()

    def test_userdata(self):

        # Create Secret
        userdata = {"key1": "val1", "key2": "val2", "key3": "val3"}
        sec = self.col.secrets.create(userdata=userdata)

        # Test Userdata
        self.assertEqual(sec.userdata, userdata)

        # Cleanup
        sec.destroy()

    def test_data(self):

        # Create Secret
        data = \
'''-----BEGIN FAKE RSA PRIVATE KEY-----
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
-----END FAKE RSA PRIVATE KEY-----'''
        sec = self.col.secrets.create(data=data)

        # Test Data
        self.assertEqual(sec.data, data)

        # Cleanup
        sec.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
