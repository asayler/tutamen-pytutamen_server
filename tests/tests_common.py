# -*- coding: utf-8 -*-


# Andy Sayler
# 2015
# Tutamen Server Tests
# Tests Common


### Imports ###

## stdlib ##
import unittest
import warnings

## pcollections ##
import pcollections.be_redis_atomic


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
