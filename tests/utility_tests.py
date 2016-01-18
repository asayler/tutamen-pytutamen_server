#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Andy Sayler
# 2016
# Tutamen Server Tests
# Utility Tests


### Imports ###

## stdlib ##
import datetime
import uuid
import unittest

## tutamen_server ##
from pytutamen_server import crypto
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

    def test_encode_decode_auth_token(self):

        def encode_decode(priv, pub, clientuid, expiration, objperm, objtype, objuid):

            token = utility.encode_auth_token(priv, clientuid, expiration,
                                              objperm, objtype, objuid)

            self.assertIsInstance(token, str)
            self.assertGreater(len(token), 0)

            val = utility.decode_auth_token(pub, token)

            self.assertIsInstance(val, dict)
            self.assertGreater(len(val), 0)

            self.assertEqual(val[utility.AUTHZ_KEY_CLIENTUID], clientuid)
            self.assertEqual(val[utility.AUTHZ_KEY_EXPIRATION], expiration)
            self.assertEqual(val[utility.AUTHZ_KEY_OBJPERM], objperm)
            self.assertEqual(val[utility.AUTHZ_KEY_OBJTYPE], objtype)
            self.assertEqual(val[utility.AUTHZ_KEY_OBJUID], objuid if objuid else None)

        pub, priv = crypto.gen_key_pair()

        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp())
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()

        # Test w/ objuid
        encode_decode(priv, pub, clientuid, expiration, objperm, objtype, objuid)

        # Test w/o objuid
        encode_decode(priv, pub, clientuid, expiration, objperm, objtype, None)

        # Test w/ blank objuid
        encode_decode(priv, pub, clientuid, expiration, objperm, objtype, "")


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
