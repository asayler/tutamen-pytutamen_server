#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Datatypes tests


### Imports ###

## stdlib ##
import uuid
import unittest

# Server Tests
import server_common

## tutamen_server ##
import tutamen_server.datatypes


### Function Classes ###

class FunctionsTestCase(server_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

    def tearDown(self):

        # Call Parent
        super().tearDown()

    def test_build_key(self):

        base_key = "test_base_key"
        prefix = "prefix"
        postfix = "postfix"
        sep = "_"

        # Test Base
        key = tutamen_server.datatypes.build_key(base_key)
        self.assertEqual(key, base_key)

        # Test Prefix
        key = tutamen_server.datatypes.build_key(base_key, prefix=prefix)
        self.assertEqual(key, (prefix + sep + base_key))

        # Test Postfix
        key = tutamen_server.datatypes.build_key(base_key, postfix=postfix)
        self.assertEqual(key, (base_key + sep + postfix))

        # Test All
        key = tutamen_server.datatypes.build_key(base_key, prefix=prefix, postfix=postfix)
        self.assertEqual(key, (prefix + sep + base_key + sep + postfix))


### Object Classes ###

class PersistentObjectServerTestCase(server_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

    def tearDown(self):

        # Call Parent
        super().tearDown()

    def test_init_and_destroy(self):

        # Create Server
        srv = tutamen_server.datatypes.PersistentObjectServer(self.driver)
        self.assertIsInstance(srv, tutamen_server.datatypes.PersistentObjectServer)

        # Cleanup
        srv.destroy()

    def test_driver(self):

        # Create Server
        srv = tutamen_server.datatypes.PersistentObjectServer(self.driver)

        # Test Driver
        self.assertIs(srv.driver, self.driver)

        # Cleanup
        srv.destroy()

    def test_objects(self):

        # Create Server
        srv = tutamen_server.datatypes.PersistentObjectServer(self.driver)
        objs = []

        # Test Empty
        self.assertEqual(len(srv.objects), len(objs))

        # Add Objects
        for i in range(10):
            key = "test_object_{}".format(i)
            objs.append(tutamen_server.datatypes.PersistentObject(srv, key=key, create=True))

        # Test Populated
        self.assertEqual(len(srv.objects), len(objs))

        # Cleanup
        for obj in objs:
            obj.destroy()
        srv.destroy()

    def test_exists(self):

        # Create Server
        srv = tutamen_server.datatypes.PersistentObjectServer(self.driver)
        objs = []

        # Add Objects
        for i in range(10):
            key = "test_object_{}".format(i)
            objs.append(tutamen_server.datatypes.PersistentObject(srv, key=key, create=True))

        # Test Exists
        for obj in objs:
            self.assertTrue(srv.exists(obj.key))

        # Cleanup Objects
        for obj in objs:
            obj.destroy()

        # Test DNE
        for obj in objs:
            self.assertFalse(srv.exists(obj.key))

        # Cleanup
        srv.destroy()

class PersistentObjectTestCase(server_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.srv = tutamen_server.datatypes.PersistentObjectServer(self.driver)

    def tearDown(self):

        # Teardown Properties
        self.srv.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create_new(self):

        # Test No Key
        self.assertRaises(TypeError, tutamen_server.datatypes.PersistentObject, self.srv)

        # Test DNE
        key = "test_object"
        self.assertRaises(tutamen_server.datatypes.ObjectDNE,
                          tutamen_server.datatypes.PersistentObject,
                          self.srv, key=key, create=False)

        # Test Create Object
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_create_existing(self):

        # Create Object
        key = "test_object"
        tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_create_overwrite(self):

        # Create Object
        key = "test_object"
        tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True, overwrite=True)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_init_existing(self):

        # Create Object
        key = "test_object"
        tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=False)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_exists(self):

        # Create Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test Exists
        self.assertTrue(obj.exists())

        # Cleanup
        obj.destroy()

        # Test DNE
        self.assertFalse(obj.exists())

    def test_key(self):

        # Create Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test key
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()

    def test_srv(self):

        # Create Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test key
        self.assertEqual(obj.srv, self.srv)

        # Cleanup
        obj.destroy()

    def test_indexes(self):

        # Create Indexed Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test Empty
        self.assertEqual(len(obj.indexes), 0)

        # Create Indexes
        indexes = []
        for i in range(10):
            key = "test_index_{}".format(i)
            indexes.append(tutamen_server.datatypes.Index(self.srv, key=key, create=True))

        # Test Populate (via Index.add())
        cnt = len(obj.indexes)
        for index in indexes:
            self.assertEqual(len(obj.indexes), cnt)
            cnt += 1
            index.add(obj)
            self.assertIn(index.key, obj.indexes)
            self.assertIn(obj.key, index.members)
            self.assertEqual(len(obj.indexes), cnt)

        # Test Depopulate (via Index.remove())
        cnt = len(obj.indexes)
        for index in indexes:
            self.assertEqual(len(obj.indexes), cnt)
            cnt -= 1
            index.remove(obj)
            self.assertNotIn(index.key, obj.indexes)
            self.assertNotIn(obj.key, index.members)
            self.assertEqual(len(obj.indexes), cnt)

        # Cleanup
        obj.destroy()
        for index in indexes:
            index.destroy()

    def test_destroy(self):

        # Create Indexed Object
        key = "test_indexed_obj"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)

        # Create Indexes
        indexes = []
        for i in range(10):
            key = "test_index_{}".format(i)
            index = tutamen_server.datatypes.Index(self.srv, key=key, create=True)
            index.add(obj)
            indexes.append(index)

        # Test Destroy
        obj.destroy()
        for index in indexes:
            self.assertNotIn(obj.key, index.members)

        # Cleanup
        for index in indexes:
            index.destroy()

class UUIDObjectTestCase(server_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.srv = tutamen_server.datatypes.PersistentObjectServer(self.driver)

    def tearDown(self):

        # Teardown Properties
        self.srv.destroy()

        # Call Parent
        super().tearDown()

    def test_init_new(self):

        # Test Bad Key Type
        key = "TestKey"
        self.assertRaises(TypeError, tutamen_server.datatypes.UUIDObject,
                          self.srv, key=key)

        # Test Create Object
        obj = tutamen_server.datatypes.UUIDObject(self.srv, create=True)
        self.assertIsInstance(obj, tutamen_server.datatypes.UUIDObject)
        self.assertIsInstance(obj.key, uuid.UUID)

        # Cleanup
        obj.destroy()

    def test_init_existing(self):

        # Create Object
        key = tutamen_server.datatypes.UUIDObject(self.srv, create=True).key
        obj = tutamen_server.datatypes.UUIDObject(self.srv, key=key, create=True)
        self.assertIsInstance(obj, tutamen_server.datatypes.UUIDObject)
        self.assertEqual(obj.key, key)

        # Cleanup
        obj.destroy()


class IndexTestCase(server_common.BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.srv = tutamen_server.datatypes.PersistentObjectServer(self.driver)

    def tearDown(self):

        # Teardown Properties
        self.srv.destroy()

        # Call Parent
        super().tearDown()

    def test_init_create_new(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=True)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_init_create_existing(self):

        # Create Index
        key = "test_index"
        tutamen_server.datatypes.Index(self.srv, key=key, create=True)
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=True)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_init_create_overwrite(self):

        # Create Index
        key = "test_index"
        tutamen_server.datatypes.Index(self.srv, key=key, create=True)
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=True, overwrite=True)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_init_existing(self):

        # Create Index
        key = "test_index"
        tutamen_server.datatypes.Index(self.srv, key=key, create=True)
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=False)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)
        self.assertEqual(index.key, key)

        # Cleanup
        index.destroy()

    def test_members(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=True)

        # Create Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test Members - Empty
        self.assertEqual(len(index.members), 0)

        # Add Member
        index.add(obj)

        # Test Members - Non-empty
        self.assertEqual(len(index.members), 1)

        # Cleanup
        obj.destroy()
        index.destroy()

    def test_is_member(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=True)

        # Create Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)

        # Test is_member() - False
        self.assertFalse(index.is_member(obj.key))

        # Add Member
        index.add(obj)

        # Test is_member() - True
        self.assertTrue(index.is_member(obj.key))

        # Cleanup
        obj.destroy()
        index.destroy()

    def test_add(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_indexed_obj_{}".format(i)
            objs.append(tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True))

        # Test Add
        cnt = 0
        for obj in objs:
            cnt += 1
            index.add(obj)
            self.assertIn(obj.key, index.members)
            self.assertIn(index.key, obj.indexes)
            self.assertEqual(len(index.members), cnt)

        # Cleanup
        index.destroy()
        for obj in objs:
            obj.destroy()

    def test_remove(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_object_{}".format(i)
            obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)
            objs.append(obj)
            index.add(obj)

        # Test Remove
        cnt = len(index.members)
        for obj in objs:
            cnt -= 1
            index.remove(obj)
            self.assertNotIn(obj.key, index.members)
            self.assertNotIn(index.key, obj.indexes)
            self.assertEqual(len(index.members), cnt)

        # Cleanup
        index.destroy()
        for obj in objs:
            obj.destroy()

    def test_destroy(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key=key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_indexed_obj_{}".format(i)
            obj = tutamen_server.datatypes.PersistentObject(self.srv, key=key, create=True)
            objs.append(obj)
            index.add(obj)

        # Test Destroy
        index.destroy()
        for obj in objs:
            self.assertNotIn(index.key, obj.indexes)

        # Cleanup
        for obj in objs:
            obj.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
