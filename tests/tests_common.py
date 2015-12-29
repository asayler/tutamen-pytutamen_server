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
from pcollections import drivers
from pcollections import backends


### Globals ###

_REDIS_DB = 9


### Exceptions ###

class TestException(Exception):
    """Base class for Test Exceptions"""
    pass

class RedisDatabaseNotEmpty(TestException):

    def __init__(self, redis):
        msg = "Redis DB not empty: {:d} keys".format(redis.dbsize())
        super().__init__(msg)


### Base Class ###

class BaseTestCase(unittest.TestCase):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.driver = drivers.RedisDriver(db=_REDIS_DB)
        self.backend = backends.RedisBaseBackend(self.driver)

    def setUp(self):

        # Call Parent
        super().setUp()

        # Confirm Empty DB
        if (self.driver.redis.dbsize() != 0):
            raise RedisDatabaseNotEmpty(self.driver.redis)

    def tearDown(self):

        # Confirm Empty DB
        if (self.driver.redis.dbsize() != 0):
            print("")
            warnings.warn("Redis database not empty prior to tearDown")
            self.driver.redis.flushdb()

        # Call Parent
        super().tearDown()
