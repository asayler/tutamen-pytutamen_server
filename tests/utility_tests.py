#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2016
# Tutamen Server Tests
# Utility Tests


### Imports ###

## stdlib ##
import uuid
import unittest

## tutamen_server ##
from pytutamen_server import utility

## Tests Common ##
import tests_common


### Function Classes ###

class UtilityTestCase(tests_common.BaseTestCase):

    def test_check_isinstance(self):

        # Test Fail
        self.assertRaises(TypeError, utility.check_isinstance, 1, str)

        # Test Pass
        utility.check_isinstance("test", str)

    def test_check_issubclass(self):

        class substr(str):
            pass

        # Test Fail
        self.assertRaises(TypeError, utility.check_issubclass, object, str)

        # Test Pass
        utility.check_issubclass(substr, str)

    def test_nos(self):

        self.assertEqual(utility.nos(None), None)
        self.assertEqual(utility.nos("test"), "test")
        self.assertEqual(utility.nos(1), str(1))


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
