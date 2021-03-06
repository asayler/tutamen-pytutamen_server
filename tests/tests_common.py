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
        self.pdriver = drivers.RedisDriver(db=_REDIS_DB)
        self.pbackend = backends.RedisBaseBackend(self.pdriver)

    def setUp(self):

        # Call Parent
        super().setUp()

        # Confirm Empty DB
        if (self.pdriver.redis.dbsize() != 0):
            raise RedisDatabaseNotEmpty(self.pdriver.redis)

    def tearDown(self):

        # Confirm Empty DB
        if (self.pdriver.redis.dbsize() != 0):
            msg = "\nRedis DB not empty: {:d} keys".format(self.pdriver.redis.dbsize())
            msg += "\n{}".format(self.pdriver.redis.keys("*"))
            warnings.warn(msg)
            self.pdriver.redis.flushdb()

        # Call Parent
        super().tearDown()
