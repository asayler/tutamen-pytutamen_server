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
import logging

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

        def encode_decode(priv, pub, accountuid, clientuid, expiration, objperm, objtype, objuid):

            token = utility.encode_auth_token(priv, accountuid, clientuid, expiration,
                                              objperm, objtype, objuid)

            self.assertIsInstance(token, str)
            self.assertGreater(len(token), 0)

            val = utility.decode_auth_token(pub, token)

            self.assertIsInstance(val, dict)
            self.assertGreater(len(val), 0)

            self.assertEqual(val[utility.AUTHZ_KEY_ACCOUNTUID], accountuid)
            self.assertEqual(val[utility.AUTHZ_KEY_CLIENTUID], clientuid)
            self.assertEqual(val[utility.AUTHZ_KEY_EXPIRATION], expiration)
            self.assertEqual(val[utility.AUTHZ_KEY_OBJPERM], objperm)
            self.assertEqual(val[utility.AUTHZ_KEY_OBJTYPE], objtype)
            self.assertEqual(val[utility.AUTHZ_KEY_OBJUID], objuid if objuid else None)

        pub, priv = crypto.gen_key_pair()

        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp())
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()

        # Test w/ objuid
        encode_decode(priv, pub, accountuid, clientuid, expiration, objperm, objtype, objuid)

        # Test w/o objuid
        encode_decode(priv, pub, accountuid, clientuid, expiration, objperm, objtype, None)

        # Test w/ blank objuid
        encode_decode(priv, pub, accountuid, clientuid, expiration, objperm, objtype, "")

    def test_verify_auth_token_sigkey(self):

        # Setup Key Pair
        pub1, priv1 = crypto.gen_key_pair()
        pub2, priv2 = crypto.gen_key_pair()

        # Test Verify - Pass
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                          objperm, objtype, objuid)
        out = utility.verify_auth_token_sigkey(token, pub1, objperm, objtype, objuid)
        self.assertTrue(out)

        # Test Verify - Fail (bad sig)
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) - 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token = utility.encode_auth_token(priv2, accountuid, clientuid, expiration,
                                          objperm, objtype, objuid)
        out = utility.verify_auth_token_sigkey(token, pub1, objperm, objtype, objuid)
        self.assertFalse(out)

        # Test Verify - Fail (expiration)
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) - 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                          objperm, objtype, objuid)
        out = utility.verify_auth_token_sigkey(token, pub1, objperm, objtype, objuid)
        self.assertFalse(out)

        # Test Verify - Fail (objperm)
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm1 = "test_perm1"
        objperm2 = "test_perm2"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                          objperm1, objtype, objuid)
        out = utility.verify_auth_token_sigkey(token, pub1, objperm2, objtype, objuid)
        self.assertFalse(out)

        # Test Verify - Fail (objtype)
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype1 = "test_obj1"
        objtype2 = "test_obj2"
        objuid = uuid.uuid4()
        token = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                          objperm, objtype1, objuid)
        out = utility.verify_auth_token_sigkey(token, pub1, objperm, objtype2, objuid)
        self.assertFalse(out)

        # Test Verify - Fail (objuid)
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid1 = uuid.uuid4()
        objuid2 = uuid.uuid4()
        token = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                          objperm, objtype, objuid1)
        out = utility.verify_auth_token_sigkey(token, pub1, objperm, objtype, objuid2)
        self.assertFalse(out)

    def test_verify_auth_token_servers(self):

        # Setup Key Pair
        pub1, priv1 = crypto.gen_key_pair()
        pub2, priv2 = crypto.gen_key_pair()

        # Setup Servers
        servers = ['https://test.server']
        manager = utility.SigkeyManager()

        # Test Verify - Pass
        manager.cache[servers[0]] = pub1
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                          objperm, objtype, objuid)
        out = utility.verify_auth_token_servers(token, servers, objperm, objtype, objuid,
                                                manager=manager)
        self.assertEqual(out, servers[0])

        # Test Verify - Fail (no servers)
        manager.cache[servers[0]] = pub1
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) - 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                          objperm, objtype, objuid)
        out = utility.verify_auth_token_servers(token, [], objperm, objtype, objuid,
                                                manager=manager)
        self.assertIsNone(out)

        # Test Verify - Fail (bad sig)
        manager.cache[servers[0]] = pub1
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) - 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token = utility.encode_auth_token(priv2, accountuid, clientuid, expiration,
                                          objperm, objtype, objuid)
        out = utility.verify_auth_token_servers(token, servers, objperm, objtype, objuid,
                                                manager=manager)
        self.assertIsNone(out)

    def test_verify_auth_token_list(self):

        # Setup Key Pair
        pub1, priv1 = crypto.gen_key_pair()
        pub2, priv2 = crypto.gen_key_pair()
        pub3, priv3 = crypto.gen_key_pair()

        # Setup Servers
        servers = ['https://test.server.one', 'https://test.server.two']
        manager = utility.SigkeyManager()

        # Test Verify - Pass (Single)
        manager.cache[servers[0]] = pub1
        manager.cache[servers[1]] = pub2
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token1 = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        token2 = utility.encode_auth_token(priv2, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        tokens = [token1, token2]
        cnt = utility.verify_auth_token_list(tokens, servers, 1,
                                             objperm, objtype, objuid,
                                             manager=manager)
        self.assertEqual(cnt, 1)

        # Test Verify - Pass (Multiple)
        manager.cache[servers[0]] = pub1
        manager.cache[servers[1]] = pub2
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token1 = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        token2 = utility.encode_auth_token(priv2, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        tokens = [token1, token2]
        cnt = utility.verify_auth_token_list(tokens, servers, 2,
                                             objperm, objtype, objuid,
                                             manager=manager)
        self.assertEqual(cnt, 2)

        # Test Verify - Pass (Bad tokens)
        manager.cache[servers[0]] = pub1
        manager.cache[servers[1]] = pub2
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token1 = utility.encode_auth_token(priv2, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        token2 = utility.encode_auth_token(priv3, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        tokens = [token1, token2]
        cnt = utility.verify_auth_token_list(tokens, servers, 1,
                                             objperm, objtype, objuid,
                                             manager=manager)
        self.assertEqual(cnt, 1)

        # Test Verify - Fail (Not enough tokens)
        manager.cache[servers[0]] = pub1
        manager.cache[servers[1]] = pub2
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token1 = utility.encode_auth_token(priv1, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        token2 = utility.encode_auth_token(priv2, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        tokens = [token1, token2]
        self.assertRaises(utility.TokenVerificationFailed, utility.verify_auth_token_list,
                          tokens, servers, 3, objperm, objtype, objuid, manager=manager)

        # Test Verify - Fail (Bad tokens)
        manager.cache[servers[0]] = pub1
        manager.cache[servers[1]] = pub2
        accountuid = uuid.uuid4()
        clientuid = uuid.uuid4()
        expiration = int(datetime.datetime.now().timestamp()) + 60
        expiration = datetime.datetime.fromtimestamp(expiration)
        objperm = "test_perm"
        objtype = "test_obj"
        objuid = uuid.uuid4()
        token1 = utility.encode_auth_token(priv2, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        token2 = utility.encode_auth_token(priv3, accountuid, clientuid, expiration,
                                           objperm, objtype, objuid)
        tokens = [token1, token2]
        self.assertRaises(utility.TokenVerificationFailed, utility.verify_auth_token_list,
                          tokens, servers, 2, objperm, objtype, objuid, manager=manager)


### Main ###

if __name__ == '__main__':
    unittest.main(warnings="always")
