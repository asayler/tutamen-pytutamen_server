#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Tests


### Imports ###

## stdlib ##
import unittest
import warnings

## pcollections ##
import pcollections.be_redis_atomic

## tutamen_server ##
import tutamen_server.storage


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

class StorageServerTestCase(BaseTestCase):

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

    def test_init(self):

        # Create Server
        ss = tutamen_server.storage.StorageServer(self.driver)
        self.assertIsNotNone(ss)
        self.assertIsInstance(ss, tutamen_server.storage.StorageServer)

        # Cleanup
        ss.wipe()


class SecretTestCase(BaseTestCase):

    def __init__(self, *args, **kwargs):

        # Call Parent
        super().__init__(*args, **kwargs)

        # Setup Properties
        self.ss = tutamen_server.storage.StorageServer(self.driver)

    def test_secret_from_new(self):

        d = "Test Secret"
        s = self.ss.secret_from_new(d)
        self.assertIsNotNone(s)
        self.assertIsInstance(s, tutamen_server.storage.Secret)


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
