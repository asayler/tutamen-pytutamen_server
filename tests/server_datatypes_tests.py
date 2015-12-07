#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Datatypes tests

### Imports ###

## stdlib ##
import unittest
import warnings

## pcollections ##
import pcollections.be_redis_atomic

## tutamen_server ##
import tutamen_server.datatypes


### Globals ###

_REDIS_DB = 9


### Exceptions ###

class TestException(Exception):
    """Base class for Test Exceptions"""
    pass

class RedisDatabaseNotEmpty(TestException):

    def __init__(self, driver):
        msg = "Redis DB not empty: {:d} keys".format(driver.dbsize())
        super().__init__(msg)

### Base Class ###

class BaseTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.driver = pcollections.be_redis_atomic.Driver(db=_REDIS_DB)

    def setUp(self):

        # Call Parent
        super().setUp()

        # Confirm Empty DB
        if (self.driver.dbsize() != 0):
            raise RedisDatabaseNotEmpty(self.driver)

    def tearDown(self):

        # Confirm Empty DB
        if (self.driver.dbsize() != 0):
            print("")
            warnings.warn("Redis database not empty prior to tearDown")
            self.driver.flushdb()

        # Call Parent
        super().tearDown()


### Object Classes ###

class PersistentObjectServerTestCase(BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

    def tearDown(self):

        # Call Parent
        super().tearDown()

    def test_init(self):

        # Create Index
        srv = tutamen_server.datatypes.PersistentObjectServer(self.driver)
        self.assertIsInstance(srv, tutamen_server.datatypes.PersistentObjectServer)

        # Cleanup
        srv.destroy()

class PersistentObjectTestCase(BaseTestCase):

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

        # Create Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True, overwrite=False)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)

        # Cleanup
        obj.destroy()

    def test_init_create_existing(self):

        # Create Object
        key = "test_object"
        tutamen_server.datatypes.PersistentObject(self.srv, key, create=True, overwrite=False)
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True, overwrite=False)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)

        # Cleanup
        obj.destroy()

    def test_init_create_overwrite(self):

        # Create Object
        key = "test_object"
        tutamen_server.datatypes.PersistentObject(self.srv, key, create=True, overwrite=False)
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True, overwrite=True)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)

        # Cleanup
        obj.destroy()

    def test_init_existing(self):

        # Create Object
        key = "test_object"
        tutamen_server.datatypes.PersistentObject(self.srv, key, create=True, overwrite=False)
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=False, overwrite=False)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)

        # Cleanup
        obj.destroy()

    def test_indexes_empty(self):

        # Create Indexed Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True)

        # Test Members
        self.assertEqual(len(obj.indexes), 1)

        # Cleanup
        obj.destroy()

    def test_indexes_populate(self):

        # Create Indexed Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True)

        # Create Indexes
        indexes = []
        for i in range(10):
            key = "test_index_{}".format(i)
            indexes.append(tutamen_server.datatypes.Index(self.srv, key, create=True))

        # Test Populate (via Index.add())
        cnt = len(obj.indexes)
        for index in indexes:
            self.assertEqual(len(obj.indexes), cnt)
            cnt += 1
            index.add(obj)
            self.assertIn(index.key, obj.indexes)
            self.assertIn(obj.key, index.members)
            self.assertEqual(len(obj.indexes), cnt)

        # Cleanup
        obj.destroy()
        for index in indexes:
            index.destroy()

    def test_indexes_depopulate(self):

        # Create Indexed Object
        key = "test_object"
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True)

       # Create Indexes
        indexes = []
        for i in range(10):
            key = "test_index_{}".format(i)
            index = tutamen_server.datatypes.Index(self.srv, key, create=True)
            index.add(obj)
            indexes.append(index)

        # Test Depopulate (via Index.remove())
        cnt = len(obj.indexes)
        for index in indexes:
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
        obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True)

        # Create Indexes
        indexes = []
        for i in range(10):
            key = "test_index_{}".format(i)
            index = tutamen_server.datatypes.Index(self.srv, key, create=True)
            index.add(obj)
            indexes.append(index)

        # Test Destroy
        obj.destroy()
        for index in indexes:
            self.assertNotIn(obj.key, index.members)

        # Cleanup
        for index in indexes:
            index.destroy()

class IndexTestCase(BaseTestCase):

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
        index = tutamen_server.datatypes.Index(self.srv, key, create=True)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)

        # Cleanup
        index.destroy()

    def test_init_create_existing(self):

        # Create Index
        key = "test_index"
        tutamen_server.datatypes.Index(self.srv, key, create=True)
        index = tutamen_server.datatypes.Index(self.srv, key, create=True)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)

        # Cleanup
        index.destroy()

    def test_init_create_overwrite(self):

        # Create Index
        key = "test_index"
        tutamen_server.datatypes.Index(self.srv, key, create=True)
        index = tutamen_server.datatypes.Index(self.srv, key, create=True, overwrite=True)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)

        # Cleanup
        index.destroy()

    def test_init_existing(self):

        # Create Index
        key = "test_index"
        tutamen_server.datatypes.Index(self.srv, key, create=True)
        index = tutamen_server.datatypes.Index(self.srv, key, create=False)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)

        # Cleanup
        index.destroy()

    def test_members_empty(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key, create=True)

        # Test Members
        self.assertEqual(len(index.members), 0)

        # Cleanup
        index.destroy()

    def test_add(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_indexed_obj_{}".format(i)
            objs.append(tutamen_server.datatypes.PersistentObject(self.srv, key, create=True))

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
        index = tutamen_server.datatypes.Index(self.srv, key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_object_{}".format(i)
            obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True)
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
        index = tutamen_server.datatypes.Index(self.srv, key, create=True)

        # Create Indexed Object
        objs = []
        for i in range(10):
            key = "test_indexed_obj_{}".format(i)
            obj = tutamen_server.datatypes.PersistentObject(self.srv, key, create=True)
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
