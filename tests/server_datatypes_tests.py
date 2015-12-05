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


### Dummy Test Objects ###

class TestPersistentObjectServer(tutamen_server.datatypes.PersistentObjectServer):

    def destroy(self):
        pass

class TestPersistentObject(tutamen_server.datatypes.PersistentObject):

    def destroy(self):
        pass


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

    def test_init_and_destroy(self):

        # Create Index
        srv = TestPersistentObjectServer(self.driver)
        self.assertIsInstance(srv, tutamen_server.datatypes.PersistentObjectServer)

        # Cleanup
        srv.destroy()

class PersistentObjectTestCase(BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.srv = TestPersistentObjectServer(self.driver)

    def tearDown(self):

        # Teardown Properties
        self.srv.destroy()

        # Call Parent
        super().tearDown()

    def test_init_and_destroy(self):

        # Create Object
        key = "test_object"
        obj = TestPersistentObject(self.srv, key)
        self.assertIsInstance(obj, tutamen_server.datatypes.PersistentObject)

        # Cleanup
        obj.destroy()

class IndexTestCase(BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.srv = TestPersistentObjectServer(self.driver)

    def tearDown(self):

        # Teardown Properties
        self.srv.destroy()

        # Call Parent
        super().tearDown()

    def test_init_and_destroy(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key)
        self.assertIsInstance(index, tutamen_server.datatypes.Index)

        # Cleanup
        index.destroy()

    def test_members_empty(self):

        # Create Index
        key = "test_index"
        index = tutamen_server.datatypes.Index(self.srv, key)

        # Test Members
        members = index.members()
        self.assertEqual(len(members), 0)

        # Cleanup
        index.destroy()

class IndexedTestCase(BaseTestCase):

    def setUp(self):

        # Call Parent
        super().setUp()

        # Setup Properties
        self.srv = TestPersistentObjectServer(self.driver)
        self.index_key = "test_index"
        self.index = tutamen_server.datatypes.Index(self.srv, self.index_key)

    def tearDown(self):

        # Teardown Properties
        self.index.destroy()
        self.srv.destroy()

        # Call Parent
        super().tearDown()

    def test_init_and_destroy(self):

        # Create Indexed Object
        key = "test_indexed_obj"
        obj = tutamen_server.datatypes.Indexed(self.srv, key)
        self.assertIsInstance(obj, tutamen_server.datatypes.Indexed)

        # Cleanup
        obj.destroy()


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
